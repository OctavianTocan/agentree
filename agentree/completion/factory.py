"""Factory for selecting a structured completion client at runtime."""

from agentree.completion.claude import ClaudeCompletionClient
from agentree.completion.codex import CodexCompletionClient
from agentree.completion.disabled import DisabledCompletionClient
from agentree.completion.protocol import StructuredCompletionClient
from agentree.config import settings
from agentree.types.aliases import CompletionClientAlias


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
  if provider == 'codex':
    return CodexCompletionClient()
  msg = f'Invalid completion client: {provider!r}'
  raise ValueError(msg)
