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
  'gpt-5.6-sol',
  'gpt-5.6-terra',
  'gpt-5.6-luna',
  'gpt-5.5',
  'gpt-5.4',
  'gpt-5.4-mini',
  'gpt-5.3-codex-spark',
]
"""Model slugs accepted by the Codex SDK's `model` option.

A convenience allowlist, not enforced by the SDK: the live catalog is fetched
per account from the backend (`AsyncCodex.models()`), so which of these a run
accepts depends on that account's entitlements. `gpt-5.6-sol` is the backend
default; the project pins `gpt-5.5` instead because the gpt-5.6 line dropped
`personality` support, which the Codex adapter sets on every turn.
"""

CodexReasoningEffortAlias = Literal[
  'none',
  'minimal',
  'low',
  'medium',
  'high',
  'xhigh',
  'max',
  'ultra',
]
"""Reasoning-effort levels accepted by the Codex SDK's `effort` option.

Supersets the SDK's `ReasoningEffort` enum (which stops at `xhigh`): the gpt-5.6
line added `max` and `ultra`, which the SDK only accepts via its forward-compat
`_missing_` hook. Kept as an explicit Literal so a typo is rejected at config
load rather than silently minted into an invalid effort the backend then throws
on. Which levels a given model honors depends on the model.
"""
