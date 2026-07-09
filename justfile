run *args:
  uv run agentree {{args}}

# Install agentree onto PATH via uv tool (editable; code changes apply immediately).
install-cli:
  uv tool install -e . --force

fmt:
  uv run ruff format agentree tests

lint:
  uv run ruff check agentree tests

typecheck:
  uv run ty check agentree tests

check:
  uv run ruff format --check agentree tests
  uv run ruff check agentree tests
  uv run ty check agentree tests
  uv run pytest -q
