"""Generic, task-agnostic wrapper for one-shot structured completions over the Claude Agent SDK."""

import dataclasses
from typing import Any, Literal, TypedDict

from claude_agent_sdk import (
  AssistantMessage,
  ClaudeAgentOptions,
  TextBlock,
  ToolUseBlock,
  query,
)
from loguru import logger

from pdfindex.config import settings
from pdfindex.types.completion import ResponseModel


class JsonSchemaOutputFormat(TypedDict):
  """The `output_format` shape the CLI expects in order to enforce structured output.

  The SDK types `output_format` as a bare `dict[str, Any]`, so nothing catches a
  wrong key here at the SDK layer - that's exactly the shape of bug this type exists
  to prevent on our side (`schema`, not `json_schema`).
  """

  type: Literal['json_schema']
  schema: dict[str, Any]


DISALLOWED_TOOLS: list[str] = [
  'ToolSearch',
  'Bash',
  'Read',
  'Write',
  'Edit',
  'Glob',
  'Grep',
  'WebFetch',
  'WebSearch',
  'NotebookEdit',
  'TodoWrite',
  'Task',
  'BashOutput',
  'KillShell',
  'ExitPlanMode',
  'Skill',
]

DEFAULT_OPTIONS = ClaudeAgentOptions(
  model=settings.claude_model,
  max_turns=1,
  thinking={'type': 'disabled'},
  setting_sources=[],
  disallowed_tools=DISALLOWED_TOOLS,
)
"""Baseline options for a single-turn, no-tool-loop structured completion.

Callers should derive their own options with
`dataclasses.replace(DEFAULT_OPTIONS, system_prompt=..., model=...)` rather than
building a `ClaudeAgentOptions` from scratch.
"""


def strip_json_fence(response: str) -> str:
  """Remove a markdown JSON fence.

  Removes a ```json ... ``` (or bare ``` ... ```) fence wrapped around a model
  response, if present.
  """
  text = response.strip()
  if text.startswith('```'):
    _, _, text = text.partition('\n')
    text = text.removesuffix('```')
  return text.strip()


async def _collect_claude_reply(
  prompt: str,
  options: ClaudeAgentOptions,
) -> tuple[str, dict[str, Any] | None]:
  """Collect text and/or StructuredOutput payload from one Claude query.

  Args:
    prompt: The user-turn text sent to the model.
    options: SDK options for the query.

  Returns:
    `(response_text, structured_output)` where `structured_output` is set when
    the model used the StructuredOutput tool.

  """
  response_text = ''
  structured_output: dict[str, Any] | None = None

  try:
    async for message in query(prompt=prompt, options=options):
      if not isinstance(message, AssistantMessage):
        continue
      for block in message.content:
        if isinstance(block, TextBlock):
          response_text += block.text
        elif isinstance(block, ToolUseBlock) and block.name == 'StructuredOutput':
          structured_output = block.input
  except Exception:
    if not response_text and structured_output is None:
      logger.exception('Claude query failed before any reply was captured')
      raise
    logger.opt(exception=True).debug('Claude error ignored because a reply was already captured')

  return response_text, structured_output


def _parse_claude_reply(
  response_model: type[ResponseModel],
  response_text: str,
  structured_output: dict[str, Any] | None,
) -> ResponseModel:
  """Validate Claude's reply against `response_model`, with pretty failure logs.

  Args:
    response_model: Pydantic model the reply must validate against.
    response_text: Concatenated text blocks from the assistant.
    structured_output: StructuredOutput tool input, if present.

  Returns:
    A validated `response_model` instance.

  """
  try:
    if structured_output is not None:
      return response_model.model_validate(structured_output)
    return response_model.model_validate_json(strip_json_fence(response_text))
  except Exception:
    logger.exception('Validation error for Claude response')
    if structured_output is not None:
      logger.debug('Claude structured_output (raw):\n{}', structured_output)
    else:
      logger.debug('Claude response_text (raw):\n{}', response_text)
    raise


async def generate_structured_completion(
  prompt: str,
  options: ClaudeAgentOptions,
  response_model: type[ResponseModel],
) -> ResponseModel:
  """Run one non-interactive Claude Agent SDK query and validate its reply against a schema.

  Args:
    prompt: The user-turn text sent to the model.
    options: SDK options for the query. Its `output_format` is overridden to
      enforce `response_model`'s schema, regardless of what's set here.
    response_model: Pydantic model the reply's JSON must validate against.

  Returns:
    An instance of `response_model` parsed from the model's reply.

  """
  output_format: JsonSchemaOutputFormat = {
    'type': 'json_schema',
    'schema': response_model.model_json_schema(),
  }
  options = dataclasses.replace(options, output_format=output_format)

  response_text, structured_output = await _collect_claude_reply(prompt, options)
  parsed = _parse_claude_reply(response_model, response_text, structured_output)
  logger.debug('Claude final_response:\n{}', parsed.model_dump_json(indent=2))
  return parsed
