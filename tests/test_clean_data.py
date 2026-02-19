from src.clean_data import unicode_normalization


# ============================================================
# unicode_normalization tests
# ============================================================


def test_nfc_combining_characters():
    """e + combining acute accent should become é."""
    text = "caf\u0065\u0301"  # e + combining acute = é
    result = unicode_normalization(text)
    assert "\u00e9" in result  # precomposed é


def test_remove_bom():
    text = "\ufeffHello world"
    result = unicode_normalization(text)
    assert result == "Hello world"


def test_remove_zero_width_space():
    text = "hel\u200blo wor\u200bld"
    result = unicode_normalization(text)
    assert result == "hello world"


def test_remove_zero_width_joiner():
    text = "some\u200dtext\u200chere"
    result = unicode_normalization(text)
    assert result == "sometexthere"


def test_remove_control_characters():
    text = "hello\x00world\x01foo\x02bar"
    result = unicode_normalization(text)
    assert result == "helloworld foobar" or result == "helloworldfoobar"
    assert "\x00" not in result
    assert "\x01" not in result
    assert "\x02" not in result


def test_preserve_newlines():
    text = "line one\nline two\nline three"
    result = unicode_normalization(text)
    assert result == "line one\nline two\nline three"


def test_tabs_normalized_to_space():
    """Tabs are normalized to single spaces (no semantic value for embeddings)."""
    text = "col1\tcol2\tcol3"
    result = unicode_normalization(text)
    assert result == "col1 col2 col3"


def test_collapse_multiple_spaces():
    text = "hello     world   foo"
    result = unicode_normalization(text)
    assert result == "hello world foo"


def test_collapse_multiple_blank_lines():
    text = "paragraph one\n\n\n\n\nparagraph two"
    result = unicode_normalization(text)
    assert result == "paragraph one\n\nparagraph two"


def test_two_newlines_preserved():
    """Exactly two newlines (one blank line) should not be collapsed."""
    text = "a\n\nb"
    result = unicode_normalization(text)
    assert result == "a\n\nb"


def test_empty_string():
    result = unicode_normalization("")
    assert result == ""


def test_already_clean_text():
    text = "This is a normal sentence with no issues."
    result = unicode_normalization(text)
    assert result == text


def test_mixed_garbage():
    """Simulate text extracted from a bad PDF scan."""
    text = "\ufeff\u200bHello\x00  \x01 \u200dworld\n\n\n\nfoo"
    result = unicode_normalization(text)
    assert "Hello" in result
    assert "world" in result
    assert "foo" in result
    assert "\x00" not in result
    assert "\ufeff" not in result
    assert "\u200b" not in result
    # Multiple blank lines collapsed
    assert "\n\n\n" not in result
