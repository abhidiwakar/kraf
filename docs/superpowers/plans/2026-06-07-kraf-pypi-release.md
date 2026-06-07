# kraf PyPI Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare `kraf` for public PyPI publishing by fixing generated Docker, Makefile, and environment behavior before release.

**Architecture:** Keep pack selection as-is and improve rendering/templates at the existing boundaries. Makefile generation remains centralized in `renderer.py`; Docker Compose remains a Jinja template; database environment values remain in database packs.

**Tech Stack:** Python 3.11, Typer, Jinja2, pytest, Ruff, Hatchling/build, PyPI.

---

### Task 1: Generator Behavior Fixes

**Files:**
- Modify: `tests/test_renderer.py`
- Modify: `src/project_initializer/renderer.py`
- Modify: `src/project_initializer/packs/docker/templates/docker-compose.yml.j2`
- Modify: `src/project_initializer/packs/database_postgres/pack.yaml`

- [ ] **Step 1: Write failing tests**

Add renderer assertions that generated projects include:
- A platform-aware Makefile using `python` on Windows and `python3` elsewhere.
- `make install` creates `.venv` before installing dependencies.
- Docker Compose includes a `db` Postgres service and points app env at `POSTGRES_HOST=db` for PostgreSQL projects.
- Django/PostgreSQL `.env.example` emits split `POSTGRES_*` variables instead of only `DATABASE_URL`.

- [ ] **Step 2: Run focused tests and verify failure**

Run: `uv run --extra dev pytest tests/test_renderer.py -v`

- [ ] **Step 3: Implement renderer/template changes**

Update Makefile rendering, Postgres env values, and Docker Compose template.

- [ ] **Step 4: Verify generator behavior**

Run: `uv run --extra dev pytest tests/test_renderer.py -v`

### Task 2: Release Verification and Publish

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README install command**

Change install docs to `pipx install kraf`.

- [ ] **Step 2: Run full verification**

Run:
- `uv run --extra dev pytest -v`
- `uv run --extra dev ruff check src tests`
- `python3 -m build`
- install the wheel in a temp venv and verify `kraf --version`

- [ ] **Step 3: Publish**

Upload to PyPI using the account/token provided by the project owner.

- [ ] **Step 4: Commit and push**

Commit the generator and docs changes, then push `main`.
