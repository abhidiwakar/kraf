import pytest

from project_initializer.errors import InvalidProjectNameError
from project_initializer.name_utils import normalize_package_name, normalize_project_slug


def test_normalize_project_slug():
    assert normalize_project_slug("Customer API") == "customer-api"


def test_normalize_package_name():
    assert normalize_package_name("Customer API") == "customer_api"


def test_package_name_cannot_start_with_digit():
    with pytest.raises(InvalidProjectNameError, match="valid Python package"):
        normalize_package_name("123 API")


def test_package_name_rejects_empty_input():
    with pytest.raises(InvalidProjectNameError, match="Project name is required"):
        normalize_package_name("   ")
