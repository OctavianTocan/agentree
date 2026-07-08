"""Factory for selecting a structured completion client at runtime."""

from pdfindex.completion.claude import ClaudeCompletionClient
from pdfindex.completion.codex import CodexCompletionClient
from pdfindex.completion.protocol import StructuredCompletionClient
from pdfindex.config import settings
from pdfindex.types.aliases import CompletionClientAlias


def create_completion_client(
  provider: CompletionClientAlias | None = None,
) -> StructuredCompletionClient:
  """Return the configured structured-completion adapter.

  Args:
    provider: Optional override. When omitted, uses `settings.completion_client`.

  Returns:
    A concrete adapter implementing `StructuredCompletionClient`.

  Raises:
    ValueError: If `provider` is not a known client alias.

  """
  provider = provider or settings.completion_client

  if provider == 'claude':
    return ClaudeCompletionClient()
  if provider == 'codex':
    return CodexCompletionClient()

  raise ValueError(f'Invalid completion client: {provider!r}')
