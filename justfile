example:
  uv run main.py --pdf_path "examples/documents/Oh_Naruto_Naruto.pdf"

fmt:
  uv run ruff format pdfindex main.py tests

lint:
  uv run ruff check pdfindex main.py tests

typecheck:
  uv run ty check pdfindex main.py tests

check:
  uv run ruff format --check pdfindex main.py tests
  uv run ruff check pdfindex main.py tests
  uv run ty check pdfindex main.py tests
  uv run pytest -q
