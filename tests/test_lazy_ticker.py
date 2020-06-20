import pytest
import tomlkit
import lazy_ticker
from lazy_ticker.paths import PROJECT_ROOT


def test_check_version():
    pyproject_path = PROJECT_ROOT / "pyproject.toml"

    assert lazy_ticker.__version__ == "0.1.0"
    assert pyproject_path.exists()

    with open(pyproject_path, mode="r") as read_file:
        pyproject_info = tomlkit.parse(read_file.read())
        assert pyproject_info["tool"]["poetry"]["version"] == lazy_ticker.__version__
