"""Reflow Markdown prose so that each sentence sits on its own line.

Block structure (paragraphs, list items, block quotes, headings, tables, code,
HTML, link reference definitions) comes from a CommonMark parser, so only the
lines of real paragraphs are ever touched. Inside a paragraph, wrapped sentences
are joined back onto one line and lines holding several sentences are split.
"""

import dataclasses
import re

from markdown_it import MarkdownIt

DEFAULT_ABBREVIATIONS: frozenset[str] = frozenset(
    {
        # Latin
        "e.g.",
        "i.e.",
        "etc.",
        "al.",
        "cf.",
        "viz.",
        "vs.",
        "v.",
        "ca.",
        "c.",
        "approx.",
        "resp.",
        "ibid.",
        "op.",
        "n.b.",
        "seq.",
        # Cross references
        "fig.",
        "figs.",
        "tab.",
        "tabs.",
        "eq.",
        "eqs.",
        "ref.",
        "refs.",
        "sec.",
        "secs.",
        "ch.",
        "app.",
        "suppl.",
        "vol.",
        "vols.",
        "no.",
        "nos.",
        "p.",
        "pp.",
        "ed.",
        "eds.",
        # Titles
        "dr.",
        "mr.",
        "mrs.",
        "ms.",
        "prof.",
        "st.",
        "jr.",
        "sr.",
        # Other
        "inc.",
        "ltd.",
        "co.",
        "corp.",
        "dept.",
        "univ.",
        "min.",
        "max.",
        "avg.",
        "est.",
        "misc.",
        "a.k.a.",
        "jan.",
        "feb.",
        "mar.",
        "apr.",
        "jun.",
        "jul.",
        "aug.",
        "sep.",
        "sept.",
        "oct.",
        "nov.",
        "dec.",
    }
)

# Closing characters that may follow the punctuation that ends a sentence or a line.
TRAILING_CLOSERS = "\"')]*_`’”"
# Characters that may begin a new sentence after the punctuation and whitespace.
_OPENERS = "\"'([*_`“‘"


@dataclasses.dataclass(frozen=True)
class Options:
    """What counts as a line and a sentence."""

    #: Split lines inside list items as well. By default a list item keeps all of
    #: its sentences on one line and only wrapped lines are joined.
    split_lists: bool = False
    #: An existing line break after one of these characters is kept, so the next
    #: line is not joined onto it. Sentences are only ever split after ``.``, ``!``
    #: and ``?``; add ``:`` and ``;`` here to also allow line breaks after them.
    keep_breaks_after: str = ".!?"
    #: Words ending in a period that do not end a sentence, lowercase.
    abbreviations: frozenset[str] = DEFAULT_ABBREVIATIONS


DEFAULT_OPTIONS = Options()


@dataclasses.dataclass(frozen=True)
class Problem:
    """One thing that was wrong with a file; ``line`` is 1-based."""

    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.line}: {self.message}"


@dataclasses.dataclass(frozen=True)
class Result:
    text: str
    problems: tuple[Problem, ...]


_PARSER = MarkdownIt("commonmark").enable("table").enable("strikethrough")

# First line of a paragraph that starts a list item: any mix of block quote
# markers and list markers, each followed by whitespace.
_ITEM_PREFIX_RE = re.compile(r"^(?:[ \t]*(?:>|(?:[-*+]|\d{1,9}[.)])(?=[ \t])))*[ \t]*")
# Any other paragraph line: indentation and block quote markers only.
_LINE_PREFIX_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*")

_BOUNDARY_RE = re.compile(r"[.!?]+[\"')\]*_`’”]*(\s+)")
# A bold lead-in such as "**Figure 3.**" or "__Note:__". It must not itself contain a
# sentence boundary, otherwise it is a bold sentence and may be split after.
_BOLD_LABEL_RE = re.compile(r"(\*\*|__)(?:(?![.!?]\s)[^*_])+(\*\*|__)[.!?]?[\"')\]\u2019\u201d]*")
_DOTTED_ABBREVIATION_RE = re.compile(r"(?:[^\W\d_]\.){2,}")
_INITIAL_RE = re.compile(r"[^\W\d_]\.")
_ENUMERATOR_RE = re.compile(r"\W*\d+[.)]")

# Inline constructs whose punctuation never ends a sentence. Each is masked with
# characters of the same length so that positions in the masked text match the
# original.
_CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->")
_ANGLE_RE = re.compile(r"<[^<>\s][^<>]*>")
_LINK_DESTINATION_RE = re.compile(r"\]\((?:[^()\s]|\([^()\s]*\))*\)")
_REFERENCE_LABEL_RE = re.compile(r"\]\[[^\]]*\]")
_URL_RE = re.compile(r"(?:https?|ftp)://[^\s<>\"']+?(?=[.,;:!?)\]]*(?:\s|$))")
_MATH_RE = re.compile(r"\$[^$\s][^$]*\$")


def _mask_inline(text: str, /) -> str:
    """Replace the inside of inline code, links, HTML, URLs and math with ``x``."""

    def keep_edges(match: re.Match[str], edge: int) -> str:
        whole = match.group()
        inner = len(whole) - 2 * edge
        return whole[:edge] + "x" * inner + whole[len(whole) - edge :]

    text = _CODE_SPAN_RE.sub(lambda m: m.group(1) + "x" * len(m.group(2)) + m.group(1), text)
    text = _HTML_COMMENT_RE.sub(lambda m: "x" * len(m.group()), text)
    text = _ANGLE_RE.sub(lambda m: "x" * len(m.group()), text)
    text = _LINK_DESTINATION_RE.sub(lambda m: keep_edges(m, 2), text)
    text = _REFERENCE_LABEL_RE.sub(lambda m: keep_edges(m, 2), text)
    text = _URL_RE.sub(lambda m: "x" * len(m.group()), text)
    text = _MATH_RE.sub(lambda m: "x" * len(m.group()), text)
    return text


def split_sentences(text: str, /, *, options: Options = DEFAULT_OPTIONS) -> list[str]:
    """Split one line of Markdown prose into its sentences."""
    masked = _mask_inline(text)
    sentences: list[str] = []
    start = 0
    for match in _BOUNDARY_RE.finditer(masked):
        if match.end() >= len(masked):
            break
        following = masked[match.end()]
        if not (following.isupper() or following.isdigit() or following in _OPENERS):
            continue
        chunk = masked[start : match.start(1)]
        if chunk.count("**") % 2 or chunk.count("__") % 2:
            continue
        if chunk.count("[") != chunk.count("]") or chunk.count("(") != chunk.count(")"):
            continue
        if _BOLD_LABEL_RE.fullmatch(chunk.strip()):
            continue
        words = chunk.split()
        last = words[-1].lstrip("(\"'[*_“‘").rstrip(TRAILING_CLOSERS) if words else ""
        if len(words) == 1 and _ENUMERATOR_RE.fullmatch(last):
            continue
        if last.lower() in options.abbreviations:
            continue
        if _DOTTED_ABBREVIATION_RE.fullmatch(last) or _INITIAL_RE.fullmatch(last):
            continue
        sentences.append(text[start : match.start(1)])
        start = match.end(1)
    sentences.append(text[start:])
    return sentences


def _front_matter_length(lines: list[str], /) -> int:
    """Number of leading lines taken by YAML or TOML front matter, or 0."""
    if not lines:
        return 0
    opener = lines[0].strip()
    if opener == "---":
        closers = ("---", "...")
    elif opener == "+++":
        closers = ("+++",)
    else:
        return 0
    for index in range(1, len(lines)):
        if lines[index].strip() in closers:
            return index + 1
    return 0


@dataclasses.dataclass(frozen=True)
class _Paragraph:
    start: int
    end: int
    in_list: bool
    starts_item: bool


def _paragraphs(lines: list[str], /) -> list[_Paragraph]:
    skip = _front_matter_length(lines)
    source = "\n".join([""] * skip + lines[skip:]) + "\n"
    tokens = _PARSER.parse(source)
    item_starts = {token.map[0] for token in tokens if token.type == "list_item_open" and token.map}
    paragraphs = []
    list_depth = 0
    for token in tokens:
        if token.type in ("bullet_list_open", "ordered_list_open"):
            list_depth += 1
        elif token.type in ("bullet_list_close", "ordered_list_close"):
            list_depth -= 1
        elif token.type == "paragraph_open" and token.map:
            start, end = token.map
            paragraphs.append(_Paragraph(start, end, list_depth > 0, start in item_starts))
    return paragraphs


def _split_prefix(line: str, /, *, item_start: bool) -> tuple[str, str]:
    pattern = _ITEM_PREFIX_RE if item_start else _LINE_PREFIX_RE
    match = pattern.match(line)
    assert match is not None
    return line[: match.end()], line[match.end() :]


def _continuation_prefix(first_prefix: str, /) -> str:
    """Indentation for the lines after the first.

    Block quote markers stay; everything else becomes spaces.
    """
    return "".join(c if c == ">" else " " for c in first_prefix.expandtabs(4))


def _ends_with_hard_break(content: str, /) -> bool:
    if content.endswith("  "):
        return True
    stripped = content.rstrip()
    backslashes = len(stripped) - len(stripped.rstrip("\\"))
    return backslashes % 2 == 1


def _continues_sentence(content: str, /, *, options: Options) -> bool:
    """Whether the following line continues the sentence that ends on ``content``."""
    if _ends_with_hard_break(content):
        return False
    stripped = content.rstrip().rstrip(TRAILING_CLOSERS)
    return not stripped.endswith(tuple(options.keep_breaks_after))


def _reflow_paragraph(
    lines: list[str], paragraph: _Paragraph, /, *, options: Options, problems: list[Problem]
) -> list[str]:
    raw = lines[paragraph.start : paragraph.end]
    first_prefix, first_content = _split_prefix(raw[0], item_start=paragraph.starts_item)
    continuation_prefix = _continuation_prefix(first_prefix)
    contents = [first_content] + [_split_prefix(line, item_start=False)[1] for line in raw[1:]]

    joined: list[tuple[int, str]] = []
    for offset, content in enumerate(contents):
        if joined and _continues_sentence(joined[-1][1], options=options):
            first_offset, previous = joined[-1]
            problems.append(
                Problem(
                    paragraph.start + first_offset + 1,
                    f"sentence is wrapped onto line {paragraph.start + offset + 1}",
                )
            )
            joined[-1] = (first_offset, previous.rstrip() + " " + content.strip())
        else:
            joined.append((offset, content))

    out: list[str] = []
    for offset, content in joined:
        body = content.rstrip()
        trailing = content[len(body) :]
        if paragraph.in_list and not options.split_lists:
            sentences = [body]
        else:
            sentences = split_sentences(body, options=options)
        if len(sentences) > 1:
            problems.append(
                Problem(paragraph.start + offset + 1, f"line holds {len(sentences)} sentences")
            )
        sentences[-1] += trailing
        out.extend(sentences)

    return [first_prefix + out[0]] + [continuation_prefix + sentence for sentence in out[1:]]


def reflow(text: str, /, *, options: Options = DEFAULT_OPTIONS) -> Result:
    """Return the reflowed text and the problems that were found."""
    bom = "﻿" if text.startswith("﻿") else ""
    body = text[len(bom) :]
    newline = "\r\n" if "\r\n" in body else "\n"
    normalized = body.replace("\r\n", "\n")
    has_final_newline = normalized.endswith("\n")
    lines = normalized[:-1].split("\n") if has_final_newline else normalized.split("\n")

    problems: list[Problem] = []
    fixed = list(lines)
    for paragraph in reversed(_paragraphs(lines)):
        fixed[paragraph.start : paragraph.end] = _reflow_paragraph(
            lines, paragraph, options=options, problems=problems
        )
    problems.sort(key=lambda problem: problem.line)

    new_text = newline.join(fixed) + (newline if has_final_newline else "")
    return Result(text=bom + new_text, problems=tuple(problems))
