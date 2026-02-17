import os
import csv
from langchain_community.document_loaders import PyPDFLoader


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".csv"}
READER_DISPATCH = {
    ".pdf": read_pdf,
    ".txt": read_txt,
    ".md": read_md,
    ".csv": read_csv,
}

def read_dir(path: str) -> list[str]:
    """Read a directory and return a list of file paths with supported extensions.

    Supported formats: PDF, TXT, MD, CSV.
    Only returns files (not subdirectories).
    Raises FileNotFoundError if path doesn't exist.
    Raises NotADirectoryError if path is not a directory.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Directory not found: {path}")

    if not os.path.isdir(path):
        raise NotADirectoryError(f"Path is not a directory: {path}")

    files = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(entry)
            if ext in SUPPORTED_EXTENSIONS:
                files.append(full_path)

    return sorted(files)

def read_pdf(path: str) -> str:
    """Extract all text from a PDF using LangChain PyPDFLoader.

    Returns the concatenated text of every page separated by newlines.
    """
    loader = PyPDFLoader(path)
    pages = loader.load()
    return "\n".join(page.page_content for page in pages)


def read_txt(path: str) -> str:
    """Read a plain text file and return its contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_md(path: str) -> str:
    """Read a Markdown file and return its raw contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_csv(path: str) -> str:
    """Read a CSV file and return its contents as readable text.

    Each row becomes a comma-separated line (with spaces after commas).
    """
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(", ".join(row))
    return "\n".join(rows)

def read_document(doc: str) -> str:
    """Read a single document and return its raw text content.

    Dispatches to the correct reader based on file extension.
    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the path is a directory or has an unsupported extension.
    """
    if not os.path.exists(doc):
        raise FileNotFoundError(f"File not found: {doc}")

    if not os.path.isfile(doc):
        raise ValueError(f"Path is not a file: {doc}")

    _, ext = os.path.splitext(doc)
    ext = ext.lower()

    reader = READER_DISPATCH.get(ext)
    if reader is None:
        raise ValueError(f"Unsupported file extension: {ext}")

    return reader(doc)

