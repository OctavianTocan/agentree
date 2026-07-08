"""Generic, task-agnostic wrapper for one-shot structured completions over the Claude Agent SDK."""

import dataclasses
import logging
from typing import Any, Literal, TypedDict

from claude_agent_sdk import (
  AssistantMessage,
  ClaudeAgentOptions,
  TextBlock,
  ToolUseBlock,
  query,
)

from pdfindex.config import settings
from pdfindex.types.completion import ResponseModel

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

  response_text = ''
  structured_output: dict[str, Any] | None = None

  try:
    async for message in query(prompt=prompt, options=options):
      if isinstance(message, AssistantMessage):
        for block in message.content:
          logger.debug({'Claude block:': block})
          if isinstance(block, TextBlock):
            logger.debug({'Claude block text:': block.text})
            response_text += block.text
          elif isinstance(block, ToolUseBlock) and block.name == 'StructuredOutput':
            structured_output = block.input
  except Exception as e:
    if not response_text and structured_output is None:
      logger.error({'Claude error:': str(e)})
      raise e
    logger.debug({'Claude error (ignored, reply already captured):': str(e)})

  try:
    if structured_output is not None:
      return response_model.model_validate(structured_output)
    return response_model.model_validate_json(strip_json_fence(response_text))
  except Exception as e:
    logger.error({'Validation error:': str(e)})
    raise e
