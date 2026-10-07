import pytest

from md_lines import Options, reflow
from md_lines.reflow import split_sentences


def fix(text, **kwargs):
    return reflow(text, options=Options(**kwargs)).text


def test_wrapped_sentence_is_joined():
    assert fix("One sentence\nwrapped over lines.\n") == "One sentence wrapped over lines.\n"


def test_two_sentences_are_split():
    assert fix("First one. Second one.\n") == "First one.\nSecond one.\n"


def test_idempotent_on_its_own_output():
    text = "A first sentence\nthat wraps. A second one! A third?\nAnd a\nfourth.\n"
    once = fix(text)
    assert once == "A first sentence that wraps.\nA second one!\nA third?\nAnd a fourth.\n"
    assert fix(once) == once


def test_existing_break_after_sentence_end_is_kept():
    text = "Ends here.\nStarts here.\n"
    assert fix(text) == text


def test_break_after_semicolon_is_joined_by_default_and_kept_when_asked():
    text = "A clause;\nanother clause.\n"
    assert fix(text) == "A clause; another clause.\n"
    assert fix(text, keep_breaks_after=".!?;") == text


def test_problems_report_original_line_numbers():
    result = reflow("Intro\n\nOne\nwrapped. Two.\n")
    assert [str(p) for p in result.problems] == [
        "3: sentence is wrapped onto line 4",
        "3: line holds 2 sentences",
    ]


def test_list_items_keep_sentences_but_join_wrapped_lines():
    text = "- First item. Still first\n  item wrapped.\n- Second item. Also here.\n"
    assert fix(text) == "- First item. Still first item wrapped.\n- Second item. Also here.\n"


def test_split_lists_option_splits_inside_items_with_matching_indent():
    text = "- First item. Still first.\n1. Numbered. Twice.\n"
    assert fix(text, split_lists=True) == (
        "- First item.\n  Still first.\n1. Numbered.\n   Twice.\n"
    )


def test_nested_list_and_loose_item_paragraph():
    text = "- outer\n  - inner one\n    wrapped\n\n  Second paragraph of outer. Two.\n"
    assert fix(text, split_lists=True) == (
        "- outer\n  - inner one wrapped\n\n  Second paragraph of outer.\n  Two.\n"
    )


def test_block_quote_keeps_marker_on_new_lines():
    text = "> Quote one\n> continues. Quote two.\n"
    assert fix(text) == "> Quote one continues.\n> Quote two.\n"


def test_lazy_block_quote_continuation_gains_marker():
    assert fix("> Quote one\ncontinues lazily.\n") == "> Quote one continues lazily.\n"


def test_list_inside_block_quote():
    text = "> - item one\n>   wrapped. Two.\n"
    assert fix(text, split_lists=True) == "> - item one wrapped.\n>   Two.\n"


@pytest.mark.parametrize(
    "text",
    [
        "```\ncode. More code\nwrapped.\n```\n",
        "~~~python\nx = 1. y = 2\n~~~\n",
        "    indented code. Not\n    prose.\n",
        "| a | b |\n|---|---|\n| one. two | three\n",
        "# Heading one. Heading two\n",
        "Setext heading. Two\n===================\n",
        "<div>\nhtml block. Two\n</div>\n",
        "<!-- a comment. spanning\nlines -->\n",
        "[ref]: https://example.com/a.b.c\n",
        "---\ntitle: Front matter. Not prose\nauthor: x\n---\n",
        '+++\ntitle = "Toml front matter. Two"\n+++\n',
        "![alt text. more](image.png)\n",
        "***\n",
    ],
)
def test_non_prose_blocks_are_untouched(text):
    assert fix(text) == text


def test_front_matter_followed_by_prose():
    text = "---\ntitle: x\n---\n\nOne. Two.\n"
    assert fix(text) == "---\ntitle: x\n---\n\nOne.\nTwo.\n"


def test_hard_line_breaks_are_kept():
    assert fix("Line one  \nline two.\n") == "Line one  \nline two.\n"
    assert fix("Line one\\\nline two.\n") == "Line one\\\nline two.\n"
    assert fix("Not a break\\\\\nline two.\n") == "Not a break\\\\ line two.\n"


def test_continuation_line_starting_with_link_is_joined():
    text = "See the results in\n[the repo](https://example.com/r.git).\n"
    assert fix(text) == "See the results in [the repo](https://example.com/r.git).\n"


def test_punctuation_inside_inline_constructs_is_ignored():
    text = (
        "Run `a.b. Then` first. Visit https://x.y/z.html. "
        "See [Fig. 1. Caption](https://a.b/c.d). Use <https://e.f/g.h>. "
        "And $x. Y$ math. Done.\n"
    )
    assert fix(text) == (
        "Run `a.b. Then` first.\nVisit https://x.y/z.html.\n"
        "See [Fig. 1. Caption](https://a.b/c.d).\nUse <https://e.f/g.h>.\n"
        "And $x. Y$ math.\nDone.\n"
    )


def test_abbreviations_initials_and_numbers_do_not_split():
    text = (
        "Use e.g. Python or vs. Rust. By J. Smith et al. In the U.S. Agency. Version 2.0 is out.\n"
    )
    assert fix(text) == (
        "Use e.g. Python or vs. Rust.\nBy J. Smith et al. In the U.S. Agency.\nVersion 2.0 is out.\n"
    )


def test_custom_abbreviations():
    text = "See Chap. Three. Done.\n"
    assert fix(text) == "See Chap.\nThree.\nDone.\n"
    assert fix(text, abbreviations=frozenset({"chap."})) == "See Chap. Three.\nDone.\n"


def test_bold_label_and_unbalanced_markup_do_not_split():
    assert fix("**Note.** This stays. This moves.\n") == "**Note.** This stays.\nThis moves.\n"
    assert fix("**Bold. Still bold.** After.\n") == "**Bold. Still bold.**\nAfter.\n"
    assert fix("(A parenthesis. Still inside.) Outside.\n") == (
        "(A parenthesis. Still inside.)\nOutside.\n"
    )


def test_closing_quotes_and_parentheses_after_punctuation():
    assert fix('He said "Go." Then left.\n') == 'He said "Go."\nThen left.\n'
    assert fix("It works (mostly). Really.\n") == "It works (mostly).\nReally.\n"


def test_enumerator_at_line_start_is_not_a_sentence():
    assert fix("1. Not a list item because of the\\\nescape. Done.\n") != ""
    assert split_sentences("3. Item text. Second.") == ["3. Item text.", "Second."]


def test_lowercase_after_period_does_not_split():
    assert fix("Save as .md files. ok\n") == "Save as .md files. ok\n"


def test_crlf_bom_and_missing_final_newline_are_preserved():
    text = "﻿One. Two.\r\nThree\r\nwrapped."
    assert fix(text) == "﻿One.\r\nTwo.\r\nThree wrapped."


def test_empty_and_blank_inputs():
    assert fix("") == ""
    assert fix("\n\n") == "\n\n"


def test_lazy_continuation_belongs_to_the_list_item():
    # A wrapped sentence is joined; a kept break is re-indented into the item.
    assert fix("- One. Two\nlazy line.\n") == "- One. Two lazy line.\n"
    assert fix("- One. Two.\nlazy line.\n") == "- One. Two.\n  lazy line.\n"


def test_dotted_abbreviations_are_detected_without_the_list():
    assert fix("Use e.g. Python.\n", abbreviations=frozenset()) == "Use e.g. Python.\n"
