# Docling Escalation

Use Docling when lightweight PDF/DOCX extraction is not enough for the task's
structure needs. It is useful for multi-format conversion, reading order, layout,
tables, Markdown/HTML/text/JSON export, and unified document representation.

## Install

Install into the target repo only:

```bash
uv add docling
uv run python -c "import docling; print('docling dep ok')"
```

Do not install Docling globally just because a reusable skill needs it.

## CLI

Basic conversion:

```bash
uv run docling path/to/input.pdf --output .cache/docling
```

For text-based PDFs where OCR is unnecessary, prefer disabling OCR for speed:

```bash
uv run docling path/to/input.pdf --no-ocr --output .cache/docling
```

Use `uv run docling --help` in the target workspace before relying on a specific
flag set, because Docling CLI options can change across releases.

## Python API

Minimal Markdown export:

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("path/to/input.pdf")
markdown = result.document.export_to_markdown()
```

Keep Docling code behind a clear function boundary so a project can fall back to
lightweight extraction when Docling is not installed or is too slow for a batch.

## Dependency Weight

Docling is a larger dependency path than `pypdf`, `pymupdf`, `pdfplumber`, and
`python-docx`. Depending on platform and pipeline options, it can involve
PyTorch, OCR backends, and model downloads. Add it only when the task needs its
document-understanding capabilities.

For OCR-specific work, choose the engine deliberately:

- Built-in/default OCR paths may download model artifacts.
- Tesseract-based OCR requires system Tesseract and language data.
- VLM, ASR, HTML rendering, and other extras should be added only when explicitly
  required by the task.
