import dataclasses

from pydantic import BaseModel

from agentree.completion.claude_sdk import (
  DEFAULT_OPTIONS,
  generate_structured_completion,
  strip_json_fence,
)
from tests.conftest import requires_live_claude


def test_strip_json_fence_removes_json_tagged_fence() -> None:
  assert strip_json_fence('```json\n{"a": 1}\n```') == '{"a": 1}'


def test_strip_json_fence_removes_bare_fence() -> None:
  assert strip_json_fence('```\n{"a": 1}\n```') == '{"a": 1}'


def test_strip_json_fence_leaves_unfenced_text_untouched() -> None:
  assert strip_json_fence('{"a": 1}') == '{"a": 1}'


class _Greeting(BaseModel):
  word: str


@requires_live_claude
def test_generate_structured_completion_validates_against_schema() -> None:
  import asyncio

  options = dataclasses.replace(
    DEFAULT_OPTIONS,
    system_prompt='You are a test fixture. Follow instructions exactly.',
  )
  result = asyncio.run(
    generate_structured_completion("Reply with the JSON word 'hello'.", options, _Greeting)
  )

  assert result.word.strip().lower() == 'hello'
