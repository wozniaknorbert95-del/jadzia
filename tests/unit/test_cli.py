"""Unit tests for cli/ package."""

from cli import __name__ as cli_name


def test_cli_package_importable():
    assert cli_name == "cli"
