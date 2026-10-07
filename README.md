# md-lines-pre-commit

A [pre-commit](https://pre-commit.com) hook that puts each sentence of a Markdown file on its own line.
Wrapped sentences are joined back onto one line, and lines that hold several sentences are split, so diffs and reviews work sentence by sentence.
Everything that is not prose stays exactly as it is.

## Usage

Add the hook to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/CodyCBakerPhD/md-lines-pre-commit
    rev: v0.1.0
    hooks:
      - id: md-lines
```

The hook rewrites the files that need it and fails once, as pre-commit hooks that fix files do.
Review the changes, stage them, and commit again.

It also works as a command:

```sh
pip install git+https://github.com/CodyCBakerPhD/md-lines-pre-commit
md-lines README.md docs/*.md        # rewrite in place, exit 1 if anything changed
md-lines --check --diff README.md   # only report, with a diff, do not write
```

## What it changes

Only the lines of paragraphs, including paragraphs inside list items and block quotes.
Within a paragraph:

- A line that does not end with `.`, `!` or `?` (closing quotes, parentheses or emphasis markers may follow) is joined with the next line, because the sentence was wrapped.
- A line holding several sentences is split at each sentence end, when what follows starts with an uppercase letter, a digit, an opening quote, bracket or emphasis marker, or inline code.
- List items are joined but not split, so an item may hold several sentences on its line; `--split-lists` splits them too, indented to the item's text.
- Block quote markers (`>`) and list indentation are reproduced on the new lines.
- Hard line breaks (two trailing spaces or a trailing backslash) are kept.

Never touched: headings, code blocks and fences, tables, HTML blocks and comments, link reference definitions, thematic breaks, YAML or TOML front matter.
Block structure comes from a CommonMark parser ([markdown-it-py](https://github.com/executablebooks/markdown-it-py)), not from guessing at line prefixes, so a wrapped line that happens to start with a link or an emphasis marker is still recognised as the continuation of its sentence.

Sentence ends are not detected inside inline code, link destinations, autolinks, inline HTML, bare URLs or `$math$`, nor after common abbreviations (`e.g.`, `etc.`, `Fig.`, `Dr.`, months and so on), initials (`J. Smith`), dotted abbreviations (`U.S.`) or an enumerator at the start of a line (`1.`).
A bold lead-in such as `**Note.**` stays attached to the sentence it introduces, and no split happens inside unbalanced bold markers, brackets or parentheses.

Line endings (LF or CRLF), a byte order mark and a missing final newline are preserved.
Running the hook on its own output changes nothing.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `--check` | off | Report what would change and exit 1 instead of rewriting files. |
| `--diff` | off | Print a unified diff of the changes. |
| `--split-lists` | off | Split sentences inside list items as well. |
| `--keep-breaks-after CHARS` | `.!?` | Keep an existing line break after any of these characters. Add `:;` to keep breaks after colons and semicolons; sentences are never split there. |
| `--abbreviations LIST` | none | Comma-separated words ending in a period that do not end a sentence, added to the built-in list. |
| `--abbreviations-file PATH` | none | File with one such word per line; blank lines and `#` comments are ignored. |
| `--no-default-abbreviations` | off | Start from an empty abbreviation list. |
| `-q`, `--quiet` | off | Do not list the problems found. |

Pass options through pre-commit with `args`:

```yaml
      - id: md-lines
        args: ["--split-lists", "--abbreviations", "chap.,sect."]
```

Exit status is 0 when nothing needed changing, 1 when files were (or in `--check` mode would be) rewritten, and 2 when a file could not be read.

## Limitations

Sentence detection is rule based.
A sentence that ends with an abbreviation not on the list and is followed by a capitalised word is not split; add the abbreviation with `--abbreviations`.
A proper noun with an internal period, such as a product name, may be split; put it in inline code or add it as an abbreviation.
Markdown extensions outside CommonMark plus tables and strikethrough (for example footnote definitions or admonitions) are treated as ordinary paragraphs.

## Development

```sh
pip install -e ".[test]"
pytest
pre-commit run --all-files
```

The hook is used on this repository's own README through `.pre-commit-config.yaml`.
