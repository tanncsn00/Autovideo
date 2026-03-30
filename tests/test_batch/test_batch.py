import csv
import pytest
from app.services.batch import BatchProcessor, BatchStatus


@pytest.fixture
def processor():
    return BatchProcessor()


@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "topics.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["topic", "template_id", "platform", "language"])
        writer.writeheader()
        writer.writerow({"topic": "AI Trends 2026", "template_id": "tiktok-trending-facts", "platform": "tiktok", "language": "en"})
        writer.writerow({"topic": "Cooking Tips", "template_id": "", "platform": "youtube", "language": "en"})
        writer.writerow({"topic": "Stock Market", "template_id": "", "platform": "instagram", "language": "en"})
    return str(csv_path)


def test_create_job_from_csv(processor, sample_csv):
    job = processor.create_job_from_csv(sample_csv)
    assert job.total_count == 3
    assert job.items[0].topic == "AI Trends 2026"
    assert job.status == BatchStatus.PENDING


def test_create_job_from_list(processor):
    topics = [
        {"topic": "Topic 1", "platform": "tiktok"},
        {"topic": "Topic 2", "platform": "youtube"},
    ]
    job = processor.create_job_from_list(topics, name="Test Batch")
    assert job.total_count == 2
    assert job.name == "Test Batch"


def test_get_job(processor):
    topics = [{"topic": "Test"}]
    job = processor.create_job_from_list(topics)
    result = processor.get_job(job.id)
    assert result is not None
    assert result["total"] == 1


def test_list_jobs(processor):
    processor.create_job_from_list([{"topic": "A"}])
    processor.create_job_from_list([{"topic": "B"}])
    jobs = processor.list_jobs()
    assert len(jobs) == 2


def test_cancel_nonexistent(processor):
    assert processor.cancel_job("nonexistent") is False


def test_job_progress(processor):
    job = processor.create_job_from_list([{"topic": "T1"}, {"topic": "T2"}])
    assert job.progress == 0
    job.completed_count = 1
    assert job.progress == 50.0


def test_empty_topics_ignored(processor):
    topics = [{"topic": "Valid"}, {"topic": ""}, {"topic": "  "}]
    job = processor.create_job_from_list(topics)
    assert job.total_count == 1  # Only "Valid" should be included
