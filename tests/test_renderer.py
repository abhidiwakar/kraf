from pathlib import Path

import pytest

from project_initializer.config import Database, ProjectConfig, ProjectType, ToolingOptions
from project_initializer.errors import RenderError
from project_initializer.pack import PackManifest
from project_initializer.renderer import RenderedProject, render_project


def _config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        project_name="Customer API",
        project_slug="customer-api",
        package_name="customer_api",
        target_dir=tmp_path / "customer-api",
        project_type=ProjectType.FASTAPI,
        database=Database.SQLITE,
        tooling=ToolingOptions(use_docker=False, use_pytest=True, use_ruff=True),
        use_sqlalchemy=False,
        use_alembic=False,
    )


def test_render_project_writes_templates_and_merged_files(tmp_path: Path):
    pack_root = tmp_path / "packs"
    pack_dir = pack_root / "fastapi"
    template_dir = pack_dir / "templates" / "app"
    template_dir.mkdir(parents=True)
    (template_dir / "main.py.j2").write_text(
        'APP_NAME = "{{ project.project_name }}"\n',
        encoding="utf-8",
    )
    pack = PackManifest(
        name="fastapi",
        dependencies=("fastapi",),
        dev_dependencies=("pytest",),
        files=(("app/main.py.j2", "app/main.py"),),
        make_targets={"run": "uvicorn app.main:app --reload"},
        env={"APP_ENV": "local"},
    )

    result = render_project(_config(tmp_path), [(pack, pack_dir)])

    assert result == RenderedProject(path=tmp_path / "customer-api", files_written=5)
    assert (tmp_path / "customer-api" / "app" / "main.py").read_text(encoding="utf-8") == (
        'APP_NAME = "Customer API"\n'
    )
    assert "fastapi" in (tmp_path / "customer-api" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    assert "pytest" in (tmp_path / "customer-api" / "requirements-dev.txt").read_text(
        encoding="utf-8"
    )
    assert "run:" in (tmp_path / "customer-api" / "Makefile").read_text(encoding="utf-8")
    assert "APP_ENV=local" in (tmp_path / "customer-api" / ".env.example").read_text(
        encoding="utf-8"
    )


def test_render_project_rejects_non_empty_target(tmp_path: Path):
    config = _config(tmp_path)
    config.target_dir.mkdir()
    (config.target_dir / "existing.txt").write_text("data", encoding="utf-8")

    with pytest.raises(RenderError, match="already exists and is not empty"):
        render_project(config, [])


def test_render_project_rejects_unsafe_destination(tmp_path: Path):
    pack_dir = tmp_path / "packs" / "unsafe"
    template_dir = pack_dir / "templates"
    template_dir.mkdir(parents=True)
    (template_dir / "content.txt.j2").write_text("data\n", encoding="utf-8")
    pack = PackManifest(
        name="unsafe",
        files=(("content.txt.j2", "../outside.txt"),),
    )

    with pytest.raises(RenderError, match="unsafe template destination"):
        render_project(_config(tmp_path), [(pack, pack_dir)])


def test_render_project_rejects_empty_rendered_destination(tmp_path: Path):
    pack_dir = tmp_path / "packs" / "unsafe"
    template_dir = pack_dir / "templates"
    template_dir.mkdir(parents=True)
    (template_dir / "content.txt.j2").write_text("data\n", encoding="utf-8")
    pack = PackManifest(
        name="unsafe",
        files=(("content.txt.j2", "{{ '' }}"),),
    )

    with pytest.raises(RenderError, match="unsafe template destination"):
        render_project(_config(tmp_path), [(pack, pack_dir)])
