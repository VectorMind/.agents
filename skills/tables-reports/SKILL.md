---
name: tables-reports
description: Use when cleaning tabular data, parsing table-like HTML/XML, fuzzy matching labels or filenames, aggregating data, and producing CSV, Markdown, HTML, or Excel reports with CLI-backed tooling from the central .agents uv environment.
---

# Tables Reports

## Dependency Setup

Use the central `.agents` uv dependency group for the runtime tooling:

```bash
uv sync --group tables-reports
```

Verify from `.agents`:

```bash
uv run --group tables-reports python -c "import pandas, openpyxl, lxml, rapidfuzz; print('tables reports deps ok')"
```

Prefer a maintained CLI package as the long-term interface. Direct libraries in
this group are a transitional backing for ad hoc tabular workflows until that
CLI exists.

## Use Cases

- Clean CSV, JSON, spreadsheet, or extracted document tables.
- Parse table-like HTML/XML with `lxml` when standard CSV/spreadsheet readers
  are not enough.
- Match records, labels, categories, or filenames with `rapidfuzz`.
- Generate processable CSV/JSON outputs plus human-facing Markdown, HTML, or
  `.xlsx` reports.
- Style Excel workbooks with frozen panes, readable widths, wrapped text, and
  clear header formatting.

## Workflow

1. Define the source schema and expected output schema before writing report
   formatting code.
2. Normalize raw values into processable data first: dates, amounts, categories,
   identifiers, and source references.
3. Keep presentation code separate from data cleanup and aggregation.
4. Write machine-readable outputs such as CSV or JSON before formatted Excel or
   HTML reports.
5. Validate row counts, totals, unmatched records, and representative samples.

## Report Conventions

- Preserve source provenance columns where practical, such as source file, source
  row, page, or record id.
- Emit unmatched or ambiguous items as explicit review outputs instead of hiding
  them in comments.
- Make Excel exports readable but not fragile: freeze the header row, wrap long
  text, cap very wide columns, and avoid formulas unless the user needs a live
  workbook.
- Keep report generation deterministic so reruns produce comparable outputs.
