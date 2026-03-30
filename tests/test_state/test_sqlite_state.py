import json
import tempfile
import threading
import pytest


@pytest.fixture
def state():
    from app.services.state import SQLiteState
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        s = SQLiteState(f.name)
        yield s


class TestSQLiteState:
    def test_update_and_get_task(self, state):
        state.update_task("task-1", state=4, progress=50)
        task = state.get_task("task-1")
        assert task is not None
        assert task["state"] == 4
        assert task["progress"] == 50

    def test_update_task_with_kwargs(self, state):
        state.update_task("task-1", state=1, progress=100,
                         videos=["/path/video.mp4"],
                         script="test script")
        task = state.get_task("task-1")
        assert task["state"] == 1
        assert task["videos"] == ["/path/video.mp4"]
        assert task["script"] == "test script"

    def test_update_existing_task(self, state):
        state.update_task("task-1", state=4, progress=25)
        state.update_task("task-1", state=4, progress=75)
        task = state.get_task("task-1")
        assert task["progress"] == 75

    def test_get_nonexistent_task(self, state):
        assert state.get_task("nonexistent") is None

    def test_delete_task(self, state):
        state.update_task("task-1", state=4)
        state.delete_task("task-1")
        assert state.get_task("task-1") is None

    def test_delete_nonexistent_task(self, state):
        # Should not raise
        state.delete_task("nonexistent")

    def test_get_all_tasks_empty(self, state):
        tasks, total = state.get_all_tasks(1, 10)
        assert tasks == []
        assert total == 0

    def test_get_all_tasks_pagination(self, state):
        for i in range(25):
            state.update_task(f"task-{i:03d}", state=1, progress=100)

        tasks, total = state.get_all_tasks(page=1, page_size=10)
        assert len(tasks) == 10
        assert total == 25

        tasks, total = state.get_all_tasks(page=3, page_size=10)
        assert len(tasks) == 5
        assert total == 25

    def test_get_all_tasks_page_beyond(self, state):
        state.update_task("task-1", state=1)
        tasks, total = state.get_all_tasks(page=5, page_size=10)
        assert len(tasks) == 0
        assert total == 1

    def test_thread_safety(self, state):
        errors = []

        def writer(task_id):
            try:
                for i in range(50):
                    state.update_task(task_id, state=4, progress=i * 2)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(f"task-{i}",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All tasks should exist
        for i in range(5):
            task = state.get_task(f"task-{i}")
            assert task is not None

    def test_persistence(self):
        """Data persists across instances"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            from app.services.state import SQLiteState
            s1 = SQLiteState(db_path)
            s1.update_task("persist-test", state=1, progress=100)
            # Close s1's connection so s2 can open cleanly
            s1._conn.close()

            s2 = SQLiteState(db_path)
            task = s2.get_task("persist-test")
            assert task is not None
            assert task["state"] == 1
            # Close s2's connection before cleanup
            s2._conn.close()
        finally:
            os.unlink(db_path)
