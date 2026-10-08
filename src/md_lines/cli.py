"""Command line entry point, also what pre-commit runs."""

import argparse
import collections.abc
import difflib
import sys

from ._version import __version__
from .globals import DEFAULT_ABBREVIATIONS
from .models import Options
from .reflow import reflow


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md-lines",
        description=(
            "Put each sentence of a Markdown file on its own line. Wrapped sentences are "
            "joined, lines holding several sentences are split; code, tables, headings, "
            "HTML and front matter are never touched. Files that needed changes are "
            "rewritten and the exit status is 1, as pre-commit expects."
        ),
    )
    parser.add_argument("files", nargs="*", help="Markdown files to check")
    parser.add_argument("--check", action="store_true", help="only report, do not rewrite any file")
    parser.add_argument("--diff", action="store_true", help="print a unified diff of the changes")
    parser.add_argument(
        "--split-lists",
        action="store_true",
        help=(
            "also split sentences inside list items "
            "(by default an item keeps its sentences on one line)"
        ),
    )
    parser.add_argument(
        "--keep-breaks-after",
        default=".!?",
        metavar="CHARS",
        help="keep an existing line break after any of these characters (default: %(default)r)",
    )
    parser.add_argument(
        "--abbreviations",
        default="",
        metavar="LIST",
        help=(
            "comma-separated words ending in a period that do not end a sentence, "
            "added to the built-in list"
        ),
    )
    parser.add_argument(
        "--abbreviations-file",
        metavar="PATH",
        help="file with one such abbreviation per line (blank lines and # comments are ignored)",
    )
    parser.add_argument(
        "--no-default-abbreviations",
        action="store_true",
        help="start from an empty abbreviation list instead of the built-in one",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="do not list the problems found")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _options_from(args: argparse.Namespace, /) -> Options:
    abbreviations = set() if args.no_default_abbreviations else set(DEFAULT_ABBREVIATIONS)
    abbreviations.update(
        word.strip().lower() for word in args.abbreviations.split(",") if word.strip()
    )
    if args.abbreviations_file:
        with open(args.abbreviations_file, encoding="utf-8") as handle:
            for line in handle:
                word = line.split("#", 1)[0].strip().lower()
                if word:
                    abbreviations.add(word)
    return Options(
        split_lists=args.split_lists,
        keep_breaks_after=args.keep_breaks_after,
        abbreviations=sorted(abbreviations),
    )


def _read(path: str, /) -> str:
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8")


def _write(*, path: str, text: str) -> None:
    with open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))


def main(argv: collections.abc.Sequence[str] | None = None, /) -> int:
    args = _build_parser().parse_args(argv)
    options = _options_from(args)

    changed = 0
    errors = 0
    for path in args.files:
        try:
            original = _read(path)
        except (OSError, UnicodeDecodeError) as error:
            print(f"{path}: {error}", file=sys.stderr)
            errors += 1
            continue
        result = reflow(text=original, options=options)
        if result.text == original:
            continue
        changed += 1
        if not args.quiet:
            for problem in result.problems:
                print(f"{path}:{problem.line}: {problem.message}")
        if args.diff:
            sys.stdout.writelines(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    result.text.splitlines(keepends=True),
                    fromfile=path,
                    tofile=path,
                )
            )
        if not args.check:
            _write(path=path, text=result.text)

    if changed and not args.quiet:
        verb = "would be rewritten" if args.check else "rewritten"
        noun = "file" if changed == 1 else "files"
        print(f"{changed} {noun} {verb} so that each sentence is on its own line.")
    if errors:
        return 2
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
