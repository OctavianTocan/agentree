example:
  uv run main.py --pdf_path "examples/documents/2023-annual-report.pdf"

fmt:
  uv run ruff format PDFindex main.py tests

lint:
  uv run ruff check PDFindex main.py tests

typecheck:
  uv run ty check PDFindex main.py tests

check:
  uv run ruff format --check PDFindex main.py tests
  uv run ruff check PDFindex main.py tests
  uv run ty check PDFindex main.py tests
  uv run pytest -q
