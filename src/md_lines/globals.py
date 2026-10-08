"""Module-level constants: the abbreviation list, the parser and the regular expressions."""

import re

from markdown_it import MarkdownIt

from md_lines.models import Options

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
TRAILING_CLOSERS = "\"')]*_`\u2019\u201d"
# Characters that may begin a new sentence after the punctuation and whitespace.
OPENERS = "\"'([*_`\u201c\u2018"

#: Options used when none are given: the built-in abbreviation list and the defaults
#: declared in the schema. A bare ``Options()`` has no abbreviations at all.
DEFAULT_OPTIONS = Options(abbreviations=sorted(DEFAULT_ABBREVIATIONS))

PARSER = MarkdownIt("commonmark").enable("table").enable("strikethrough")

# First line of a paragraph that starts a list item: any mix of block quote markers and list
# markers, each followed by whitespace.
ITEM_PREFIX_RE = re.compile(r"^(?:[ \t]*(?:>|(?:[-*+]|\d{1,9}[.)])(?=[ \t])))*[ \t]*")
# Any other paragraph line: indentation and block quote markers only.
LINE_PREFIX_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*")

# Candidate sentence boundary: terminal punctuation, optional closers, whitespace.
BOUNDARY_RE = re.compile(r"[.!?]+[\"')\]*_`\u2019\u201d]*(\s+)")
# A bold lead-in such as "**Figure 3.**" or "__Note:__". It must not itself contain a sentence
# boundary, otherwise it is a bold sentence and may be split after.
BOLD_LABEL_RE = re.compile(r"(\*\*|__)(?:(?![.!?]\s)[^*_])+(\*\*|__)[.!?]?[\"')\]\u2019\u201d]*")
DOTTED_ABBREVIATION_RE = re.compile(r"(?:[^\W\d_]\.){2,}")
INITIAL_RE = re.compile(r"[^\W\d_]\.")
ENUMERATOR_RE = re.compile(r"\W*\d+[.)]")

# Inline constructs whose punctuation never ends a sentence. Each is masked with characters
# of the same length so that positions in the masked text match the original.
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->")
ANGLE_RE = re.compile(r"<[^<>\s][^<>]*>")
LINK_DESTINATION_RE = re.compile(r"\]\((?:[^()\s]|\([^()\s]*\))*\)")
REFERENCE_LABEL_RE = re.compile(r"\]\[[^\]]*\]")
URL_RE = re.compile(r"(?:https?|ftp)://[^\s<>\"']+?(?=[.,;:!?)\]]*(?:\s|$))")
MATH_RE = re.compile(r"\$[^$\s][^$]*\$")
