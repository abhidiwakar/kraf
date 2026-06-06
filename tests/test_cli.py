from typer.testing import CliRunner

from project_initializer.cli import app


def test_version_command_displays_package_version():
    runner = CliRunner()

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "project-init 0.1.0" in result.stdout
