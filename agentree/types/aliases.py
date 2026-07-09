"""Shared string-literal aliases for settings and SDK configuration."""

from typing import Literal

ClaudeModelAlias = Literal['haiku', 'sonnet', 'opus', 'fable']
"""Model aliases accepted by the Claude Agent SDK's `model` option."""

CompletionClientAlias = Literal['claude', 'codex']
"""Which structured-completion adapter to use at runtime."""

CodexModelAlias = Literal[
  'gpt-5.6',
  'gpt-5.5',
  'gpt-5.4-mini',
  'gpt-5.4',
  'gpt-5.3-codex-spark',
]
"""Model aliases accepted by Codex SDK's `model` option."""
