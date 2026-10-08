"""The LinkML schema is the source of the data model; models.py must match it."""

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "src" / "md_lines" / "schema" / "md_lines.yaml"
MODELS = ROOT / "src" / "md_lines" / "models.py"


def test_schema_declares_the_model_classes():
    schemaview = pytest.importorskip("linkml_runtime.utils.schemaview")
    view = schemaview.SchemaView(str(SCHEMA))
    assert {"Options", "Problem", "Result", "Paragraph"} <= set(view.all_classes())
    assert view.induced_slot("line", "Problem").required
    assert view.induced_slot("abbreviations", "Options").multivalued


def test_models_are_generated_from_the_schema():
    pythongen = pytest.importorskip("linkml.generators.pythongen")
    generated = pythongen.PythonGenerator(str(SCHEMA), metadata=False).serialize()
    assert generated.rstrip("\n") == MODELS.read_text().rstrip("\n"), (
        "src/md_lines/models.py is out of date; run "
        "`gen-python --no-metadata src/md_lines/schema/md_lines.yaml > src/md_lines/models.py`"
    )


def test_generated_defaults_match_the_schema():
    from md_lines import Options

    options = Options()
    assert options.split_lists is False
    assert options.keep_breaks_after == ".!?"
    assert options.abbreviations == []
