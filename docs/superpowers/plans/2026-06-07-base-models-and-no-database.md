# Base Models and No Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit no-database option and generate reusable base model templates for ORM-backed projects.

**Architecture:** Extend the existing `Database` enum, prompt, config normalization, and pack resolver. Keep model templates in dedicated ORM packs: Django gets an abstract base model through a `django_models` pack; FastAPI with SQLAlchemy gets `app/db/base.py` and example models inherit from it.

**Tech Stack:** Python 3.11, Typer, Jinja2 templates, pytest, Ruff.

---

### Task 1: Add No Database

**Files:**
- Modify: `src/project_initializer/config.py`
- Modify: `src/project_initializer/prompts.py`
- Modify: `src/project_initializer/pack.py`
- Modify: `src/project_initializer/renderer.py`
- Modify: `src/project_initializer/packs/docker/templates/docker-compose.yml.j2`
- Modify: `src/project_initializer/packs/django/templates/project/settings.py.j2`
- Modify: `tests/test_config.py`
- Modify: `tests/test_resolver.py`
- Modify: `tests/test_renderer.py`
- Modify: `tests/test_cli.py`

- [ ] Add `Database.NONE = "none"`.
- [ ] Add prompt option `3. No database`.
- [ ] Disable SQLAlchemy and Alembic when FastAPI uses no database.
- [ ] Do not select database packs for no-database projects.
- [ ] Render Django no-database projects with Django's dummy database backend.
- [ ] Do not render database env vars or Postgres Docker service for no-database projects.

### Task 2: Add Base Models

**Files:**
- Create: `src/project_initializer/packs/django_models/pack.yaml`
- Create: `src/project_initializer/packs/django_models/templates/core/__init__.py.j2`
- Create: `src/project_initializer/packs/django_models/templates/core/models.py.j2`
- Modify: `src/project_initializer/packs/django/templates/project/settings.py.j2`
- Modify: `src/project_initializer/packs/orm_sqlalchemy/pack.yaml`
- Create: `src/project_initializer/packs/orm_sqlalchemy/templates/app/db/base.py.j2`
- Modify: `src/project_initializer/packs/orm_sqlalchemy/templates/app/db/session.py.j2`
- Modify: `src/project_initializer/packs/orm_sqlalchemy/templates/app/db/models.py.j2`
- Modify: `tests/test_renderer.py`

- [ ] Django base model uses UUID primary key plus `created_at`, `updated_at`, nullable `deleted_at`.
- [ ] FastAPI SQLAlchemy base model uses UUID primary key plus timezone-aware timestamps and nullable `deleted_at`.
- [ ] No separate `is_deleted` column.
- [ ] FastAPI no-database projects do not generate ORM model files.

### Task 3: Verify Release Artifacts

**Files:**
- Build output: `dist/`

- [ ] Run full pytest and Ruff.
- [ ] Rebuild `dist/`.
- [ ] Install rebuilt wheel in a temporary venv.
- [ ] Generate representative projects and inspect rendered files.
