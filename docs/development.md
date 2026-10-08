# Development

```sh
pip install -e ".[dev]"
pytest
pre-commit run --all-files
```

The `dev` extra brings pytest, pre-commit and [LinkML](https://linkml.io).
The hook is used on this repository's own Markdown through `.pre-commit-config.yaml`.

## Layout

- `src/md_lines/schema/md_lines.yaml` defines the data model (`Options`, `Problem`, `Result`, `Paragraph`) as a LinkML schema.
- `src/md_lines/models.py` is generated from the schema and is not edited by hand; the formatters skip it, and a test fails when it and the schema drift apart.
- `src/md_lines/globals.py` holds the module-level constants: the abbreviation list, the parser, the regular expressions and `DEFAULT_OPTIONS`.
- `src/md_lines/reflow.py` holds the reflow functions only, and `src/md_lines/cli.py` the command.
- `__version__` is read from the installed package metadata, so `pyproject.toml` is the only place the version is written.

After changing the schema, regenerate the model:

```sh
gen-python --no-metadata src/md_lines/schema/md_lines.yaml > src/md_lines/models.py
```

## Repository checks

The pre-commit configuration follows [historia](https://github.com/CodyCBakerPhD/historia): pre-commit-hooks, check-github-workflows, black, ruff (lint plus isort rules, with `--fix`), codespell with the `en-GB_to_en-US` dictionary so the text stays in American English, and this repository's own `md-lines` hook.
CI runs the tests and the hooks on the newest Python release.

## Exit status

`md-lines` exits 0 when nothing needed changing, 1 when files were (or in `--check` mode would be) rewritten, and 2 when a file could not be read.
