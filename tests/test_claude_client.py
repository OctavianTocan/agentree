import dataclasses

import pytest
from pydantic import BaseModel

from PDFindex.claude_client import (
  DEFAULT_OPTIONS,
  generate_structured_completion,
  strip_json_fence,
)
from PDFindex.settings import settings

requires_live_claude = pytest.mark.skipif(
  not settings.claude_code_oauth_token,
  reason='requires a live Claude Agent SDK OAuth token',
)


def test_strip_json_fence_removes_json_tagged_fence():
  assert strip_json_fence('```json\n{"a": 1}\n```') == '{"a": 1}'


def test_strip_json_fence_removes_bare_fence():
  assert strip_json_fence('```\n{"a": 1}\n```') == '{"a": 1}'


def test_strip_json_fence_leaves_unfenced_text_untouched():
  assert strip_json_fence('{"a": 1}') == '{"a": 1}'


class _Greeting(BaseModel):
  word: str


@requires_live_claude
def test_generate_structured_completion_validates_against_schema():
  import asyncio

  options = dataclasses.replace(
    DEFAULT_OPTIONS, system_prompt='You are a test fixture. Follow instructions exactly.'
  )
  result = asyncio.run(
    generate_structured_completion("Reply with the JSON word 'hello'.", options, _Greeting)
  )

  assert result.word.strip().lower() == 'hello'
