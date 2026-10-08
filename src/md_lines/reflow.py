"""Reflow Markdown prose so that each sentence sits on its own line.

Block structure (paragraphs, list items, block quotes, headings, tables, code, HTML, link
reference definitions) comes from a CommonMark parser, so only the lines of real paragraphs
are ever touched. Inside a paragraph, wrapped sentences are joined back onto one line and
lines holding several sentences are split.

The data model (Options, Problem, Result, Paragraph) is generated from the LinkML schema in
``schema/md_lines.yaml``; the constants live in ``globals.py``.
"""

import re

from md_lines import globals as g
from md_lines.models import Options, Paragraph, Problem, Result


def _mask_inline(text: str, /) -> str:
    """Replace the inside of inline code, links, HTML, URLs and math with ``x``."""

    def keep_edges(match: re.Match[str], edge: int) -> str:
        whole = match.group()
        inner = len(whole) - 2 * edge
        return whole[:edge] + "x" * inner + whole[len(whole) - edge :]

    text = g.CODE_SPAN_RE.sub(lambda m: m.group(1) + "x" * len(m.group(2)) + m.group(1), text)
    text = g.HTML_COMMENT_RE.sub(lambda m: "x" * len(m.group()), text)
    text = g.ANGLE_RE.sub(lambda m: "x" * len(m.group()), text)
    text = g.LINK_DESTINATION_RE.sub(lambda m: keep_edges(m, 2), text)
    text = g.REFERENCE_LABEL_RE.sub(lambda m: keep_edges(m, 2), text)
    text = g.URL_RE.sub(lambda m: "x" * len(m.group()), text)
    text = g.MATH_RE.sub(lambda m: "x" * len(m.group()), text)
    return text


def split_sentences(text: str, /, *, options: Options = g.DEFAULT_OPTIONS) -> list[str]:
    """Split one line of Markdown prose into its sentences."""
    abbreviations = set(options.abbreviations or ())
    masked = _mask_inline(text)
    sentences: list[str] = []
    start = 0
    for match in g.BOUNDARY_RE.finditer(masked):
        if match.end() >= len(masked):
            break
        following = masked[match.end()]
        if not (following.isupper() or following.isdigit() or following in g.OPENERS):
            continue
        chunk = masked[start : match.start(1)]
        if chunk.count("**") % 2 or chunk.count("__") % 2:
            continue
        if chunk.count("[") != chunk.count("]") or chunk.count("(") != chunk.count(")"):
            continue
        if g.BOLD_LABEL_RE.fullmatch(chunk.strip()):
            continue
        words = chunk.split()
        last = words[-1].lstrip("(\"'[*_“‘").rstrip(g.TRAILING_CLOSERS) if words else ""
        if len(words) == 1 and g.ENUMERATOR_RE.fullmatch(last):
            continue
        if last.lower() in abbreviations:
            continue
        if g.DOTTED_ABBREVIATION_RE.fullmatch(last) or g.INITIAL_RE.fullmatch(last):
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


def _paragraphs(lines: list[str], /) -> list[Paragraph]:
    skip = _front_matter_length(lines)
    source = "\n".join([""] * skip + lines[skip:]) + "\n"
    tokens = g.PARSER.parse(source)
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
            paragraphs.append(
                Paragraph(
                    start=start, end=end, in_list=list_depth > 0, starts_item=start in item_starts
                )
            )
    return paragraphs


def _split_prefix(line: str, /, *, item_start: bool) -> tuple[str, str]:
    pattern = g.ITEM_PREFIX_RE if item_start else g.LINE_PREFIX_RE
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
    stripped = content.rstrip().rstrip(g.TRAILING_CLOSERS)
    return not stripped.endswith(tuple(options.keep_breaks_after or ""))


def _reflow_paragraph(
    lines: list[str], paragraph: Paragraph, /, *, options: Options, problems: list[Problem]
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
                    line=paragraph.start + first_offset + 1,
                    message=f"sentence is wrapped onto line {paragraph.start + offset + 1}",
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
                Problem(
                    line=paragraph.start + offset + 1,
                    message=f"line holds {len(sentences)} sentences",
                )
            )
        sentences[-1] += trailing
        out.extend(sentences)

    return [first_prefix + out[0]] + [continuation_prefix + sentence for sentence in out[1:]]


def reflow(text: str, /, *, options: Options = g.DEFAULT_OPTIONS) -> Result:
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
    return Result(text=bom + new_text, problems=problems)
