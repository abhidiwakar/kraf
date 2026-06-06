from project_initializer.config import Database, ProjectType, ToolingOptions, normalize_answers


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
