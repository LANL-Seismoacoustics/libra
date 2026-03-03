from importlib import resources
from importlib.resources.abc import Traversable
import yaml


def load_yaml_resource(package: str, filename: str):
    """
    Load YAML resource safely from package data.

    This works in:
        - Editable installs
        - Wheels
        - Jupyter notebooks
        - Containers
    """

    resource = resources.files(package).joinpath(filename)

    # Handle both Traversable + real file fallback
    if isinstance(resource, Traversable):
        with resource.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # Fallback (just in case)
    with open(resource, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)