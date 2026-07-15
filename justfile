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
  uv run ty check --error-on-warning agentree tests

# Fail if uv.lock has drifted from pyproject.toml.
lock-check:
  uv lock --check

check:
  uv lock --check
  uv run ruff format --check agentree tests
  uv run ruff check agentree tests
  uv run ty check --error-on-warning agentree tests
  uv run pytest -q
