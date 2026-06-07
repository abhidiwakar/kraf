from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError

from project_initializer.config import Database, ProjectConfig, ProjectType
from project_initializer.errors import RenderError
from project_initializer.pack import PackManifest


@dataclass(frozen=True)
class RenderedProject:
    path: Path
    files_written: int


PackWithPath = tuple[PackManifest, Path]


def render_project(config: ProjectConfig, packs: list[PackWithPath]) -> RenderedProject:
    _ensure_target_is_safe(config.target_dir)
    config.target_dir.mkdir(parents=True, exist_ok=True)

    files_written = 0
    for pack, pack_dir in packs:
        files_written += _render_pack_files(config, pack, pack_dir)

    files_written += _write_requirements(config.target_dir, packs)
    files_written += _write_makefile(config.target_dir, packs)
    files_written += _write_env_example(config, packs)

    return RenderedProject(path=config.target_dir, files_written=files_written)


def _ensure_target_is_safe(target_dir: Path) -> None:
    if target_dir.exists() and any(target_dir.iterdir()):
        raise RenderError(f"Target directory '{target_dir}' already exists and is not empty.")


def _render_pack_files(config: ProjectConfig, pack: PackManifest, pack_dir: Path) -> int:
    template_root = pack_dir / "templates"
    environment = Environment(
        loader=FileSystemLoader(template_root),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )

    files_written = 0
    for source, destination in pack.files:
        try:
            rendered = environment.get_template(source).render(project=config)
            rendered_destination = environment.from_string(destination).render(project=config)
        except TemplateError as exc:
            raise RenderError(
                f"Failed to render template '{source}' from pack '{pack.name}'."
            ) from exc

        destination_path = _safe_destination_path(config.target_dir, rendered_destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(rendered, encoding="utf-8")
        files_written += 1

    return files_written


def _safe_destination_path(target_dir: Path, destination: str) -> Path:
    if not destination.strip():
        raise RenderError(f"Refusing to write unsafe template destination '{destination}'.")
    destination_path = Path(destination)
    if destination_path.is_absolute() or ".." in destination_path.parts:
        raise RenderError(f"Refusing to write unsafe template destination '{destination}'.")
    return target_dir / destination_path


def _write_requirements(target_dir: Path, packs: list[PackWithPath]) -> int:
    dependencies = _unique_sorted(item for pack, _path in packs for item in pack.dependencies)
    dev_dependencies = _unique_sorted(
        item for pack, _path in packs for item in pack.dev_dependencies
    )

    (target_dir / "requirements.txt").write_text(_lines(dependencies), encoding="utf-8")
    (target_dir / "requirements-dev.txt").write_text(_lines(dev_dependencies), encoding="utf-8")
    return 2


def _write_makefile(target_dir: Path, packs: list[PackWithPath]) -> int:
    targets: dict[str, str] = {
        "install": "$(VENV_PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt",
    }
    for pack, _path in packs:
        targets.update(pack.make_targets)

    phony_targets = " ".join(["venv", *targets])
    target_blocks = [
        "venv: .venv/pyvenv.cfg\n",
        ".venv/pyvenv.cfg:\n\t$(PYTHON) -m venv .venv\n",
    ]
    target_blocks.extend(_make_target_block(name, command) for name, command in targets.items())
    content = "\n".join(
        [
            "ifeq ($(OS),Windows_NT)",
            "PYTHON ?= python",
            "VENV_PYTHON := .venv/Scripts/python.exe",
            "else",
            "PYTHON ?= python3",
            "VENV_PYTHON := .venv/bin/python",
            "endif",
            "",
            f".PHONY: {phony_targets}",
            "",
            *target_blocks,
        ]
    )
    (target_dir / "Makefile").write_text(content, encoding="utf-8")
    return 1


def _make_target_block(name: str, command: str) -> str:
    dependency = "" if name.startswith("docker-") else " .venv/pyvenv.cfg"
    return f"{name}:{dependency}\n\t{command}\n"


def _write_env_example(config: ProjectConfig, packs: list[PackWithPath]) -> int:
    env_values: dict[str, str] = {}
    for pack, _path in packs:
        env_values.update(pack.env)

    if config.database is Database.POSTGRESQL and config.project_type in {
        ProjectType.DJANGO,
        ProjectType.DJANGO_DRF,
    }:
        env_values.pop("DATABASE_URL", None)
        env_values.update(
            {
                "POSTGRES_DB": "app",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
            }
        )

    (config.target_dir / ".env.example").write_text(
        _lines(f"{key}={value}" for key, value in sorted(env_values.items())),
        encoding="utf-8",
    )
    return 1


def _unique_sorted(values: Iterable[str]) -> list[str]:
    return sorted({str(value) for value in values if str(value).strip()})


def _lines(values: Iterable[str]) -> str:
    lines = list(values)
    if not lines:
        return ""
    return "\n".join(lines) + "\n"
