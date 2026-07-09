run *args:
  uv run pdfindex {{args}}

# Install pdfindex onto PATH via uv tool (editable; code changes apply immediately).
install-cli:
  uv tool install -e . --force

fmt:
  uv run ruff format pdfindex tests

lint:
  uv run ruff check pdfindex tests

typecheck:
  uv run ty check pdfindex tests

check:
  uv run ruff format --check pdfindex tests
  uv run ruff check pdfindex tests
  uv run ty check pdfindex tests
  uv run pytest -q
