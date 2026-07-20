from collections.abc import Iterator

import pytest
from loguru import logger
from openai_codex.generated.v2_all import ThreadTokenUsage, TokenUsageBreakdown

from agentree.completion.pricing import estimate_codex_usd, log_claude_cost, log_codex_cost
from agentree.types.aliases import CODEX_PRICING, _require_complete_pricing


def _usage(*, input_tokens: int, cached: int, output: int) -> ThreadTokenUsage:
  breakdown = TokenUsageBreakdown(
    cached_input_tokens=cached,
    input_tokens=input_tokens,
    output_tokens=output,
    reasoning_output_tokens=0,
    total_tokens=input_tokens + output,
  )
  return ThreadTokenUsage(last=breakdown, total=breakdown)


@pytest.fixture
def captured_logs() -> Iterator[list[str]]:
  messages: list[str] = []
  sink_id = logger.add(messages.append, level='INFO', format='{message}')
  yield messages
  logger.remove(sink_id)


def test_estimate_codex_usd_prices_uncached_cached_and_output_separately() -> None:
  rate = CODEX_PRICING['gpt-5.5']
  assert rate is not None
  usage = _usage(input_tokens=1000, cached=200, output=500)

  # 800 uncached input + 200 cached input + 500 output, per-million.
  expected = (800 * rate.input + 200 * rate.cached_input + 500 * rate.output) / 1_000_000
  assert estimate_codex_usd('gpt-5.5', usage) == pytest.approx(expected)


def test_estimate_codex_usd_charges_cached_rate_when_all_input_is_cached() -> None:
  rate = CODEX_PRICING['gpt-5.5']
  assert rate is not None
  usage = _usage(input_tokens=400, cached=400, output=0)

  expected = 400 * rate.cached_input / 1_000_000
  assert estimate_codex_usd('gpt-5.5', usage) == pytest.approx(expected)


def test_estimate_codex_usd_returns_none_for_unpriced_model(
  monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setitem(CODEX_PRICING, 'gpt-5.5', None)

  assert estimate_codex_usd('gpt-5.5', _usage(input_tokens=10, cached=0, output=5)) is None


def test_log_codex_cost_skips_when_usage_missing(captured_logs: list[str]) -> None:
  log_codex_cost('gpt-5.5', None)

  assert captured_logs == []


def test_log_codex_cost_skips_when_model_unpriced(
  monkeypatch: pytest.MonkeyPatch, captured_logs: list[str]
) -> None:
  monkeypatch.setitem(CODEX_PRICING, 'gpt-5.5', None)

  log_codex_cost('gpt-5.5', _usage(input_tokens=10, cached=0, output=5))

  assert captured_logs == []


def test_log_codex_cost_emits_when_priced(captured_logs: list[str]) -> None:
  log_codex_cost('gpt-5.5', _usage(input_tokens=10, cached=0, output=5))

  assert any('Codex turn cost' in message for message in captured_logs)


def test_log_claude_cost_skips_when_cost_missing(captured_logs: list[str]) -> None:
  log_claude_cost(None, {'input_tokens': 10})

  assert captured_logs == []


def test_log_claude_cost_emits_when_cost_present(captured_logs: list[str]) -> None:
  log_claude_cost(0.0123, None)

  assert any('Claude query cost' in message for message in captured_logs)


def test_require_complete_pricing_passes_for_shipped_registry() -> None:
  _require_complete_pricing()


def test_require_complete_pricing_flags_a_missing_slug(monkeypatch: pytest.MonkeyPatch) -> None:
  incomplete = dict(CODEX_PRICING)
  incomplete.pop('gpt-5.5')
  monkeypatch.setattr('agentree.types.aliases.CODEX_PRICING', incomplete)

  with pytest.raises(RuntimeError, match='must have a row'):
    _require_complete_pricing()
