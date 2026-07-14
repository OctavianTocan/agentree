"""Shared string-literal aliases for settings and SDK configuration."""

from typing import Literal

ClaudeModelAlias = Literal['haiku', 'sonnet', 'opus', 'fable']
"""Short model aliases accepted by the Claude Agent SDK's `model` option."""

ClaudeModelId = Literal[
  'claude-opus-4-8',
  'claude-sonnet-5',
  'claude-haiku-4-5-20251001',
  'claude-fable-5',
]
"""Fully-qualified Claude model IDs accepted by the Claude Agent SDK's `model` option."""

CompletionClientAlias = Literal['claude', 'codex']
"""Which structured-completion adapter to use at runtime."""

CodexModelAlias = Literal[
  'gpt-5.5-pro',
  'gpt-5.5',
  'gpt-5.3-codex',
  'gpt-5.2-codex',
  'gpt-5.2',
  'gpt-5.1-codex-max',
  'gpt-5.1-codex-mini',
  'gpt-5.1',
]
"""Model slugs accepted by the Codex SDK's `model` option.

Scoped to the catalog of the binary the SDK bundles (openai-codex-cli-bin,
currently 0.137.0a4) - not the newer standalone Codex CLI, which the Python
channel lags. Bumping openai-codex may widen this set.
"""
