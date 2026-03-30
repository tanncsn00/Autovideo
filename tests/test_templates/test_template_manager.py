import json
import pytest
from pathlib import Path
from app.services.template import TemplateManager, TemplateConfig


@pytest.fixture
def template_dir(tmp_path):
    cat = tmp_path / "test-category"
    cat.mkdir()
    t = {
        "id": "test-template", "name": "Test", "description": "Test template",
        "category": "test-category", "platform": "general",
        "video_aspect": "16:9", "font_size": 48,
    }
    (cat / "test.json").write_text(json.dumps(t))
    return tmp_path


def test_load_templates(template_dir):
    mgr = TemplateManager(str(template_dir))
    templates = mgr.list_templates()
    assert len(templates) == 1
    assert templates[0]["id"] == "test-template"


def test_get_template(template_dir):
    mgr = TemplateManager(str(template_dir))
    t = mgr.get_template("test-template")
    assert t is not None
    assert t.name == "Test"


def test_get_nonexistent(template_dir):
    mgr = TemplateManager(str(template_dir))
    assert mgr.get_template("nonexistent") is None


def test_apply_template(template_dir):
    mgr = TemplateManager(str(template_dir))
    params = mgr.apply_template("test-template")
    assert params["video_aspect"] == "16:9"
    assert params["font_size"] == 48


def test_apply_with_overrides(template_dir):
    mgr = TemplateManager(str(template_dir))
    params = mgr.apply_template("test-template", overrides={"font_size": 72})
    assert params["font_size"] == 72


def test_apply_nonexistent_raises(template_dir):
    mgr = TemplateManager(str(template_dir))
    with pytest.raises(ValueError):
        mgr.apply_template("nonexistent")


def test_list_by_category(template_dir):
    mgr = TemplateManager(str(template_dir))
    assert len(mgr.list_templates(category="test-category")) == 1
    assert len(mgr.list_templates(category="other")) == 0


def test_get_categories(template_dir):
    mgr = TemplateManager(str(template_dir))
    cats = mgr.get_categories()
    assert "test-category" in cats


def test_load_real_templates():
    """Test loading actual templates from the project"""
    root = Path(__file__).parent.parent.parent / "templates"
    if root.exists():
        mgr = TemplateManager(str(root))
        templates = mgr.list_templates()
        assert len(templates) >= 10
