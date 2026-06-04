---
name: document-ingest
description: Use when extracting, converting, or auditing PDFs, DOCX files, scanned documents, images, HTML, or mixed document folders into text, Markdown, JSON, or table-friendly data. Uses staged lightweight/OCR/Docling escalation with CLI-backed tooling from the central .agents uv environment.
---

# Document Ingest

## Operating Rule

Start with the lightest extraction stage that can produce reliable output. Escalate
only when evidence from the documents shows the current stage is insufficient.

Use document-processing tooling from the central `.agents` uv environment. Do
not install document-processing dependencies globally or via `uvx`.

Prefer first-class CLI packages as the runtime boundary. Direct libraries in the
central dependency groups are a transitional backing until a maintained ingest
CLI exists. Install dependencies into the target workspace only when the target
workspace's own code must import or execute them.

## Stage 0: Inspect

- Identify formats, counts, representative file names, and whether the inputs are
  text-based or scanned.
- Prefer repo-local work directories such as `.cache/` for copied source files
  and intermediate binary artifacts.
- Prefer `data/` or another project-owned output directory for processable
  text, Markdown, JSON, CSV, and report artifacts.
- Avoid committing raw sensitive documents unless the user explicitly asks.

## Stage 1: Lightweight Extraction

Use this first for text-based PDFs and DOCX files.

Dependency group: `document-ingest-light`

Typical tools:

- `pypdf` for simple PDF metadata and fallback text extraction.
- `pymupdf` / `fitz` for fast page text, page counts, rendering diagnostics, and
  bounding-box-aware extraction.
- `pdfplumber` for layout-aware text and table-oriented extraction from
  text-based PDFs.
- `python-docx` for Word `.docx` text and paragraph/table traversal.

Quality checks:

- Compare extracted page count with source page count where possible.
- Flag pages with empty or near-empty text.
- Save small source-to-output samples when deciding whether to escalate.

## Stage 2: OCR Fallback

Use this only when PDFs or images are scanned, text is missing, or text extraction
is clearly garbled.

Dependency group: `document-ingest-ocr`

System tools may also be needed: `pdftotext`, `pdfinfo`, `tesseract`, and OCR
language packs. Ask before installing system packages.

Run OCR selectively. Prefer processing the failed files or pages instead of
rerunning the whole corpus blindly.

## Stage 3: Docling

Use Docling when the task needs stronger document understanding:

- complex layout or reading order,
- table structure extraction,
- mixed input formats with a unified representation,
- Markdown/HTML/text/lossless JSON export,
- advanced conversion workflows where lightweight extraction loses too much
  structure.

Dependency group: `document-ingest-docling`

Read `references/docling.md` before adding Docling or designing a Docling-based
workflow. Treat it as a heavier dependency path because it may pull large
transitive packages and model artifacts.

## Output Expectations

- Preserve enough provenance to connect each output row or section back to a
  source file and page where possible.
- Produce structured artifacts first, then human-facing summaries or reports.
- Include an extraction note when output quality depends on OCR, layout
  heuristics, fuzzy matching, or manual classification.
- Verify the generated data before presenting it as complete.
