"""The installed version.

It is read from the package metadata, so pyproject.toml stays the only place the version is written.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("md-lines-pre-commit")
except importlib.metadata.PackageNotFoundError:  # a checkout that was not pip-installed
    __version__ = "0+unknown"
