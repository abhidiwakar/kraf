import pytest

from project_initializer.config import Database, ProjectType, ToolingOptions, normalize_answers
from project_initializer.errors import InvalidProjectNameError


def test_normalize_django_drf_answers_selects_django_stack():
    config = normalize_answers(
        {
            "project_name": "Customer API",
            "project_type": "django_drf",
            "database": "postgresql",
            "use_docker": True,
            "use_pytest": True,
            "use_ruff": True,
            "use_sqlalchemy": False,
            "use_alembic": False,
        }
    )

    assert config.project_name == "Customer API"
    assert config.project_slug == "customer-api"
    assert config.package_name == "customer_api"
    assert config.project_type is ProjectType.DJANGO_DRF
    assert config.database is Database.POSTGRESQL
    assert config.tooling == ToolingOptions(use_docker=True, use_pytest=True, use_ruff=True)


def test_fastapi_without_sqlalchemy_disables_alembic():
    config = normalize_answers(
        {
            "project_name": "Inventory Service",
            "project_type": "fastapi",
            "database": "sqlite",
            "use_docker": False,
            "use_pytest": True,
            "use_ruff": True,
            "use_sqlalchemy": False,
            "use_alembic": True,
        }
    )

    assert config.use_sqlalchemy is False
    assert config.use_alembic is False


def test_null_project_name_is_rejected():
    with pytest.raises(InvalidProjectNameError, match="Project name is required"):
        normalize_answers(
            {
                "project_name": None,
                "project_type": "fastapi",
                "database": "sqlite",
            }
        )


def test_missing_project_name_is_rejected():
    with pytest.raises(InvalidProjectNameError, match="Project name is required"):
        normalize_answers(
            {
                "project_type": "fastapi",
                "database": "sqlite",
            }
        )


def test_non_string_project_name_is_rejected():
    with pytest.raises(InvalidProjectNameError, match="Project name must be text"):
        normalize_answers(
            {
                "project_name": 123,
                "project_type": "fastapi",
                "database": "sqlite",
            }
        )


@pytest.mark.parametrize("project_type", ["django", "django_drf"])
def test_django_stacks_disable_sqlalchemy_and_alembic(project_type):
    config = normalize_answers(
        {
            "project_name": "Customer API",
            "project_type": project_type,
            "database": "postgresql",
            "use_sqlalchemy": True,
            "use_alembic": True,
        }
    )

    assert config.use_sqlalchemy is False
    assert config.use_alembic is False


def test_fastapi_with_sqlalchemy_preserves_alembic():
    config = normalize_answers(
        {
            "project_name": "Inventory Service",
            "project_type": "fastapi",
            "database": "postgresql",
            "use_sqlalchemy": True,
            "use_alembic": True,
        }
    )

    assert config.use_sqlalchemy is True
    assert config.use_alembic is True


def test_fastapi_no_database_disables_sqlalchemy_and_alembic():
    config = normalize_answers(
        {
            "project_name": "Inventory Service",
            "project_type": "fastapi",
            "database": "none",
            "use_sqlalchemy": True,
            "use_alembic": True,
        }
    )

    assert config.database is Database.NONE
    assert config.use_sqlalchemy is False
    assert config.use_alembic is False
