"""Shared string-literal aliases for settings and SDK configuration."""

from typing import Literal, NamedTuple, get_args

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


class CodexRate(NamedTuple):
  """Per-million-token USD rates for a Codex model.

  `cached_input` prices the portion of the input that was served from cache: the
  backend bills those tokens below the normal `input` rate, and the SDK reports
  them as a subset of the input-token count rather than in addition to it.
  """

  input: float
  cached_input: float
  output: float


# Standard API rates per 1M tokens (input, cached input, output), from OpenAI's
# published pricing as of 2026-07.
CODEX_PRICING: dict[CodexModelAlias, CodexRate | None] = {
  'gpt-5.6-sol': CodexRate(input=5.00, cached_input=0.50, output=30.00),
  'gpt-5.6-terra': CodexRate(input=2.50, cached_input=0.25, output=15.00),
  'gpt-5.6-luna': CodexRate(input=1.00, cached_input=0.10, output=6.00),
  'gpt-5.5': CodexRate(input=5.00, cached_input=0.50, output=30.00),
  'gpt-5.4': CodexRate(input=2.50, cached_input=0.25, output=15.00),
  'gpt-5.4-mini': CodexRate(input=0.75, cached_input=0.075, output=4.50),
  'gpt-5.3-codex-spark': CodexRate(input=1.75, cached_input=0.175, output=14.00),
}
"""USD rates per million tokens, keyed by Codex model slug.

The single source of truth for Codex prices. `None` marks a slug we haven't
priced yet, so `estimate_codex_usd` returns None rather than guessing. Claude
costs are not listed here: the Claude SDK reports the real spend per query
(`ResultMessage.total_cost_usd`), so there is nothing to estimate.
"""


def _require_complete_pricing() -> None:
  # A slug added to CodexModelAlias must also get a price row (even if None), so
  # it can't silently fall through to "unpriced".
  if set(CODEX_PRICING) != set(get_args(CodexModelAlias)):
    msg = 'CODEX_PRICING must have a row for every CodexModelAlias slug'
    raise RuntimeError(msg)


_require_complete_pricing()


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
