"""USD cost reporting for structured completions.

Claude spend is read straight from the SDK (`ResultMessage.total_cost_usd`);
only Codex needs a rate table, because its SDK reports token counts but no
dollar figure. Prices live with the model aliases in `agentree.types.aliases`.
"""

from typing import Any

from loguru import logger
from openai_codex.generated.v2_all import ThreadTokenUsage

from agentree.types.aliases import CODEX_PRICING, CodexModelAlias


def estimate_codex_usd(model: CodexModelAlias, usage: ThreadTokenUsage) -> float | None:
  """Estimate the USD cost of a Codex turn from its token usage.

  Args:
    model: Codex model slug the turn ran on.
    usage: Token usage reported by the Codex SDK for the turn.

  Returns:
    Estimated cost in USD, or None when `model` has no rate in `CODEX_PRICING`.

  """
  rate = CODEX_PRICING.get(model)
  if rate is None:
    return None
  tokens = usage.total
  uncached_input = max(0, tokens.input_tokens - tokens.cached_input_tokens)
  return (
    uncached_input * rate.input
    + tokens.cached_input_tokens * rate.cached_input
    + tokens.output_tokens * rate.output
  ) / 1_000_000


def log_codex_cost(model: CodexModelAlias, usage: ThreadTokenUsage | None) -> None:
  """Log the estimated USD cost of a Codex turn, when it can be priced.

  Args:
    model: Codex model slug the turn ran on.
    usage: Token usage reported by the Codex SDK, or None if unavailable.

  """
  if usage is None:
    return
  est = estimate_codex_usd(model, usage)
  if est is None:
    return
  logger.bind(
    model=model,
    input_tokens=usage.total.input_tokens,
    output_tokens=usage.total.output_tokens,
    est_usd=est,
  ).info('Estimated Codex turn cost')


def log_claude_cost(total_cost_usd: float | None, usage: dict[str, Any] | None) -> None:
  """Log the actual USD cost of a Claude query as reported by the SDK.

  Args:
    total_cost_usd: Real spend for the query, or None when the SDK omits it.
    usage: Token usage the SDK attached to the result, if any.

  """
  if total_cost_usd is None:
    return
  logger.bind(usage=usage, cost_usd=total_cost_usd).info('Claude query cost')
