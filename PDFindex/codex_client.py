"""Generic structured completion wrapper using the OpenAI Codex Agent SDK."""

from typing import TypeVar

from openai_codex import AsyncCodex, CodexConfig, Sandbox
from pydantic import BaseModel

ResponseModel = TypeVar('ResponseModel', bound=BaseModel)


async def generate_structured_completion(
  prompt: str, response_model: type[ResponseModel]
) -> ResponseModel:
  """Run a one-shot query using Codex and validate the structured response against a schema.

  Args:
      prompt: The user-turn text sent to the model.
      response_model: Pydantic model class used to validate the JSON response.

  Returns:
      An instance of the validated response model.

  """
  config = CodexConfig(
    config_overrides=('agents.agent_max_turns=1',),
  )

  async with AsyncCodex(config=config) as codex:
    thread = await codex.thread_start(sandbox=Sandbox.read_only)
    result = await thread.run(
      input=prompt,
      output_schema=response_model.model_json_schema(),
    )
    if result.final_response is None:
      raise RuntimeError('Codex returned empty response')
    return response_model.model_validate_json(result.final_response)
