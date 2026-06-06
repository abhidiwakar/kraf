import keyword
import re

from project_initializer.errors import InvalidProjectNameError

_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")
_MULTIPLE_DASHES = re.compile(r"-+")
_MULTIPLE_UNDERSCORES = re.compile(r"_+")


def normalize_project_slug(project_name: str) -> str:
    cleaned = project_name.strip()
    if not cleaned:
        raise InvalidProjectNameError("Project name is required.")

    slug = _NON_ALNUM.sub("-", cleaned).strip("-").lower()
    slug = _MULTIPLE_DASHES.sub("-", slug)
    if not slug:
        raise InvalidProjectNameError("Project name must contain letters or numbers.")
    return slug


def normalize_package_name(project_name: str) -> str:
    cleaned = project_name.strip()
    if not cleaned:
        raise InvalidProjectNameError("Project name is required.")

    package_name = _NON_ALNUM.sub("_", cleaned).strip("_").lower()
    package_name = _MULTIPLE_UNDERSCORES.sub("_", package_name)

    if not package_name or not package_name.isidentifier() or keyword.iskeyword(package_name):
        raise InvalidProjectNameError(
            f"Project name '{project_name}' cannot be converted into a valid Python package name."
        )

    return package_name
