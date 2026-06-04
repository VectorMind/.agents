---
name: uv-workspace-deps
description: Use when Python dependencies for reusable skills or local scripts must be installed into the current repo's uv-managed project environment, not globally, not in agent configuration folders, not in the reusable skills repo, and not via uvx. Provides dependency profiles for document ingest, OCR, Docling, tables/reports, CLI tooling, and dev tools.
---

# UV Workspace Dependencies

## Core Rule

Install Python dependencies in the target workspace that will run the code. Do not
install skill runtime dependencies globally, in agent configuration folders, in
the reusable skills repository, or through `uvx`.

Use `uv add` from the target repo root so `pyproject.toml`, `uv.lock`, and the
repo-local `.venv` are updated together.

## Workflow

1. Identify the target workspace root. Prefer `git rev-parse --show-toplevel`
   when the task is inside a git repo.
2. Confirm that the target has a `pyproject.toml`. If it does not, ask before
   initializing one with `uv init --bare`, then add `[tool.uv] package = false`
   for scripts-only workspaces.
3. Select the smallest dependency profile that satisfies the task.
4. Run `uv add ...` in the target workspace.
5. Verify with `uv run python -c "import ..."` from the target workspace.
6. Keep system packages separate from Python packages. Check for system tools
   with `command -v` or equivalent, and ask before installing OS packages.

If another skill asks for one of these profiles, use the profile as the source of
truth for dependency installation.

## Profiles

`document-ingest-light`

- Use for text-based PDFs, basic PDF metadata/text fallback, PDF layout text,
  and DOCX text extraction.
- Install:

```bash
uv add "pypdf>=5.0.0" "pymupdf>=1.24.0" "pdfplumber>=0.11.0" "python-docx>=1.1.0"
```

- Verify:

```bash
uv run python -c "import pypdf, fitz, pdfplumber, docx; print('document ingest light deps ok')"
```

`document-ingest-ocr`

- Use only after detecting scanned pages or unusable text extraction.
- Includes `document-ingest-light`.
- Install:

```bash
uv add "pypdf>=5.0.0" "pymupdf>=1.24.0" "pdfplumber>=0.11.0" "python-docx>=1.1.0"
uv add "pdf2image>=1.17.0" "pillow>=11.0.0" "pytesseract>=0.3.13"
```

- Verify Python imports:

```bash
uv run python -c "import pdf2image, PIL, pytesseract; print('ocr python deps ok')"
```

- Typical system tools: `pdftotext`, `pdfinfo`, `tesseract`, language packs
  such as `tesseract-ocr-eng` or `tesseract-ocr-deu`.

`document-ingest-docling`

- Use when document layout, reading order, tables, multi-format conversion, or
  Markdown/JSON document representation justify a heavier dependency.
- Install:

```bash
uv add docling
```

- Verify:

```bash
uv run python -c "import docling; print('docling dep ok')"
```

- Treat Docling as an escalation path. It may pull in large transitive
  dependencies such as PyTorch and may download models depending on pipeline and
  OCR options.

`tables-reports`

- Use for tabular cleanup, matching, aggregation, CSV/Markdown/HTML reports, and
  `.xlsx` generation.
- Install:

```bash
uv add "pandas>=2.2.0" "openpyxl>=3.1.0" "lxml>=5.0.0" "rapidfuzz>=3.10.0"
```

- Verify:

```bash
uv run python -c "import pandas, openpyxl, lxml, rapidfuzz; print('tables reports deps ok')"
```

`cli`

- Use when a reusable local script needs command-line arguments and structured
  terminal output.
- Install:

```bash
uv add "typer>=0.15.0" "rich>=13.0.0"
```

`dev`

- Use for tests, linting, and notebooks in the target workspace.
- Install:

```bash
uv add --dev "pytest>=8.3.0" "ruff>=0.8.0" "ipykernel>=6.29.0"
```

## Optional Helper

This skill includes `scripts/ensure_uv_workspace_deps.py` for profile lookup,
dry-run command generation, installation, and import checks. Run it from the
target workspace, using the script path from this skill directory:

```bash
python <skill-dir>/scripts/ensure_uv_workspace_deps.py list
python <skill-dir>/scripts/ensure_uv_workspace_deps.py install document-ingest-light --dry-run
python <skill-dir>/scripts/ensure_uv_workspace_deps.py check document-ingest-light
```

The helper never installs global packages. It only shells out to `uv add` in the
current working directory.
