"""Put each Markdown sentence on its own line."""

from importlib.metadata import PackageNotFoundError, version

from md_lines.globals import DEFAULT_ABBREVIATIONS, DEFAULT_OPTIONS
from md_lines.models import Options, Paragraph, Problem, Result
from md_lines.reflow import reflow, split_sentences

__all__ = [
    "DEFAULT_ABBREVIATIONS",
    "DEFAULT_OPTIONS",
    "Options",
    "Paragraph",
    "Problem",
    "Result",
    "__version__",
    "reflow",
    "split_sentences",
]

try:
    # The version lives in pyproject.toml only; the installed metadata carries it.
    __version__ = version("md-lines-pre-commit")
except PackageNotFoundError:  # running from a checkout that was not pip-installed
    __version__ = "0+unknown"
