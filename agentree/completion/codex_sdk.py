"""Generic structured completion wrapper using the OpenAI Codex Agent SDK."""

from loguru import logger
from openai_codex import ApprovalMode, AsyncCodex, AsyncThread, Sandbox, TurnResult

from agentree.config import settings
from agentree.types.completion import ResponseModel


async def generate_structured_completion(
  prompt: str,
  response_model: type[ResponseModel],
  *,
  system_prompt: str,
) -> ResponseModel:
  """Run a one-shot query using Codex and validate the structured response against a schema.

  Args:
    prompt: The user-turn text sent to the model.
    response_model: Pydantic model class used to validate the JSON response.
    system_prompt: The system prompt to use.

  Returns:
    An instance of the validated response model.

  """
  async with AsyncCodex() as codex:
    thread: AsyncThread = await codex.thread_start(
      sandbox=Sandbox.read_only,
      model=settings.codex_model,
      approval_mode=ApprovalMode.deny_all,
      personality=settings.personality,
      base_instructions=system_prompt,
    )
    result: TurnResult = await thread.run(
      input=prompt,
      effort=settings.codex_reasoning_effort,
      output_schema=response_model.model_json_schema(),
    )
    logger.bind(status=str(result.status)).debug('Codex turn completed')
    if result.error is not None:
      logger.bind(error=str(result.error)).error('Codex turn returned an error')
    if result.final_response is None:
      raise RuntimeError('Codex returned empty response')
    try:
      parsed = response_model.model_validate_json(result.final_response)
    except Exception:
      logger.exception('Validation error for Codex response')
      logger.debug('Codex final_response (raw):\n{}', result.final_response)
      raise
    logger.debug('Codex final_response:\n{}', parsed.model_dump_json(indent=2))
    return parsed
