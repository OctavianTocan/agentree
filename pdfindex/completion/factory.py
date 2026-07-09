"""Factory for selecting a structured completion client at runtime."""

from pdfindex.completion.claude import ClaudeCompletionClient
from pdfindex.completion.codex import CodexCompletionClient
from pdfindex.completion.disabled import DisabledCompletionClient
from pdfindex.completion.protocol import StructuredCompletionClient
from pdfindex.config import settings
from pdfindex.types.aliases import CompletionClientAlias


def create_completion_client(
  provider: CompletionClientAlias | None = None,
) -> StructuredCompletionClient:
  """Return the configured structured-completion adapter.

  Args:
    provider: Optional override. When omitted, uses `settings.completion_client`.
      Ignored when `settings.completions_enabled` is false.

  Returns:
    A concrete adapter implementing `StructuredCompletionClient`.

  Raises:
    ValueError: If `provider` is not a known client alias.

  """
  if not settings.completions_enabled:
    return DisabledCompletionClient()

  provider = provider or settings.completion_client

  if provider == 'claude':
    return ClaudeCompletionClient()
  elif provider == 'codex':
    return CodexCompletionClient()
  else:
    print(f'Invalid completion client: {provider!r}')
    return DisabledCompletionClient()
