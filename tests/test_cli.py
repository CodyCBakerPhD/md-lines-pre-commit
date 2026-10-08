import subprocess
import sys

from md_lines.cli import main


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_rewrites_and_exits_one(tmp_path, capsys):
    path = write(tmp_path, "a.md", "One. Two.\n")
    assert main([str(path)]) == 1
    assert path.read_text() == "One.\nTwo.\n"
    out = capsys.readouterr().out
    assert f"{path}:1: line holds 2 sentences" in out
    assert "1 file rewritten" in out


def test_clean_file_exits_zero(tmp_path, capsys):
    path = write(tmp_path, "a.md", "One.\nTwo.\n")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == ""


def test_check_mode_does_not_write(tmp_path, capsys):
    path = write(tmp_path, "a.md", "One. Two.\n")
    assert main(["--check", str(path)]) == 1
    assert path.read_text() == "One. Two.\n"
    assert "would be rewritten" in capsys.readouterr().out


def test_diff_output(tmp_path, capsys):
    path = write(tmp_path, "a.md", "One. Two.\n")
    main(["--check", "--diff", "-q", str(path)])
    out = capsys.readouterr().out
    assert "-One. Two." in out and "+One." in out and "+Two." in out


def test_options_are_passed_through(tmp_path):
    path = write(tmp_path, "a.md", "- One. Two.\n\nSee Chap. Three.\n")
    main(["--split-lists", "--abbreviations", "chap.", str(path)])
    assert path.read_text() == "- One.\n  Two.\n\nSee Chap. Three.\n"


def test_abbreviations_file(tmp_path):
    words = write(tmp_path, "abbr.txt", "# comment\nchap.\n\n")
    path = write(tmp_path, "a.md", "See Chap. Three.\n")
    assert main(["--abbreviations-file", str(words), str(path)]) == 0


def test_no_default_abbreviations(tmp_path):
    path = write(tmp_path, "a.md", "Use etc. Python.\n")
    assert main(["--no-default-abbreviations", str(path)]) == 1
    assert path.read_text() == "Use etc.\nPython.\n"


def test_missing_file_exits_two(tmp_path, capsys):
    assert main([str(tmp_path / "missing.md")]) == 2
    assert "missing.md" in capsys.readouterr().err


def test_module_and_console_entry_points(tmp_path):
    path = write(tmp_path, "a.md", "One.\n")
    assert (
        subprocess.run([sys.executable, "-m", "md_lines", str(path)], check=False).returncode == 0
    )
    assert subprocess.run(
        ["md-lines", "--version"], capture_output=True, text=True
    ).stdout.startswith("md-lines ")


def test_version_matches_pyproject():
    import pathlib
    import re

    import md_lines

    pyproject = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    declared = re.search(r'^version = "([^"]+)"', pyproject.read_text(), re.M).group(1)
    assert md_lines.__version__ == declared
