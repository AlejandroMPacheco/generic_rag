import os
import pytest
from src.preprocessing import read_dir, read_document


@pytest.fixture
def sample_dir(tmp_path):
    """Create a temporary directory with mixed file types."""
    # Supported files
    (tmp_path / "document.pdf").write_text("fake pdf content")
    (tmp_path / "notes.txt").write_text("some notes")
    (tmp_path / "readme.md").write_text("# Title")
    (tmp_path / "data.csv").write_text("col1,col2\n1,2")

    # Unsupported files (should be ignored)
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    (tmp_path / "script.py").write_text("print('hello')")
    (tmp_path / ".hidden").write_text("hidden file")

    # Subdirectory (should be ignored)
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("nested file")

    return tmp_path


@pytest.fixture
def empty_dir(tmp_path):
    """Create an empty temporary directory."""
    empty = tmp_path / "empty"
    empty.mkdir()
    return empty


def test_read_dir_returns_only_supported_files(sample_dir):
    result = read_dir(str(sample_dir))

    filenames = [os.path.basename(f) for f in result]
    assert "document.pdf" in filenames
    assert "notes.txt" in filenames
    assert "readme.md" in filenames
    assert "data.csv" in filenames


def test_read_dir_excludes_unsupported_files(sample_dir):
    result = read_dir(str(sample_dir))

    filenames = [os.path.basename(f) for f in result]
    assert "image.png" not in filenames
    assert "script.py" not in filenames
    assert ".hidden" not in filenames


def test_read_dir_excludes_subdirectories(sample_dir):
    result = read_dir(str(sample_dir))

    # No path should point to a directory
    for path in result:
        assert os.path.isfile(path)

    # nested.txt should NOT appear (it's inside a subdirectory)
    filenames = [os.path.basename(f) for f in result]
    assert "nested.txt" not in filenames


def test_read_dir_returns_full_paths(sample_dir):
    result = read_dir(str(sample_dir))

    for path in result:
        assert os.path.isabs(path)
        assert os.path.exists(path)


def test_read_dir_returns_sorted_paths(sample_dir):
    result = read_dir(str(sample_dir))
    assert result == sorted(result)


def test_read_dir_empty_directory(empty_dir):
    result = read_dir(str(empty_dir))
    assert result == []


def test_read_dir_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        read_dir("/nonexistent/path/that/does/not/exist")


def test_read_dir_path_is_file(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("content")

    with pytest.raises(NotADirectoryError):
        read_dir(str(file_path))


def test_read_dir_returns_exactly_4_supported_files(sample_dir):
    result = read_dir(str(sample_dir))
    assert len(result) == 4


def test_read_dir_case_insensitive_extensions(tmp_path):
    """Extensions like .PDF, .Txt should also be recognized."""
    (tmp_path / "UPPER.PDF").write_text("pdf")
    (tmp_path / "Mixed.Txt").write_text("txt")

    result = read_dir(str(tmp_path))
    assert len(result) == 2

def test_read_document_txt(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("Hello world", encoding="utf-8")

    result = read_document(str(f))
    assert result == "Hello world"


def test_read_document_txt_multiline(tmp_path):
    content = "line one\nline two\nline three"
    f = tmp_path / "multi.txt"
    f.write_text(content, encoding="utf-8")

    result = read_document(str(f))
    assert result == content


def test_read_document_txt_utf8(tmp_path):
    content = "acentos: cafe, nino, arbol"
    f = tmp_path / "utf8.txt"
    f.write_text(content, encoding="utf-8")

    result = read_document(str(f))
    assert "cafe" in result


def test_read_document_markdown(tmp_path):
    content = "# Title\n\nSome **bold** text.\n\n- item 1\n- item 2"
    f = tmp_path / "doc.md"
    f.write_text(content, encoding="utf-8")

    result = read_document(str(f))
    assert result == content


def test_read_document_csv(tmp_path):
    content = "name,age,city\nAlice,30,Berlin\nBob,25,Munich"
    f = tmp_path / "data.csv"
    f.write_text(content, encoding="utf-8")

    result = read_document(str(f))
    assert "name, age, city" in result
    assert "Alice, 30, Berlin" in result
    assert "Bob, 25, Munich" in result


def test_read_document_csv_preserves_all_rows(tmp_path):
    content = "a,b\n1,2\n3,4\n5,6"
    f = tmp_path / "nums.csv"
    f.write_text(content, encoding="utf-8")

    result = read_document(str(f))
    lines = result.strip().split("\n")
    assert len(lines) == 4


def test_read_document_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")

    result = read_document(str(f))
    assert result == ""


def test_read_document_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_document("/nonexistent/file.txt")


def test_read_document_unsupported_extension(tmp_path):
    f = tmp_path / "image.png"
    f.write_bytes(b"\x89PNG")

    with pytest.raises(ValueError, match="Unsupported file extension"):
        read_document(str(f))


def test_read_document_path_is_directory(tmp_path):
    with pytest.raises(ValueError, match="not a file"):
        read_document(str(tmp_path))


def test_read_document_returns_string(tmp_path):
    f = tmp_path / "check.txt"
    f.write_text("test", encoding="utf-8")

    result = read_document(str(f))
    assert isinstance(result, str)
