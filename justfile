example:
  uv run main.py --pdf_path "PageIndex/examples/documents/2023-annual-report.pdf"

fmt:
  uv run ruff format PDFindex main.py tests

lint:
  uv run ruff check PDFindex main.py tests

typecheck:
  uv run ty check PDFindex main.py tests

check: fmt lint typecheck
  uv run pytest -q
