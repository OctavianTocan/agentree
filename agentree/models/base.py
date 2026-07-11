"""Shared Pydantic bases for Agentree schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict


def require_all_properties(schema: dict[str, Any]) -> None:
  """Ensure every property is listed in `required` for strict JSON schemas.

  Codex/OpenAI strict schemas require every property to be defined. This
  function adds a `required` property to the schema for each property.

  Args:
    schema: The schema to add the `required` property to.

  """
  if 'properties' not in schema:
    return

  schema['required'] = list(schema['properties'].keys())


class StrictModel(BaseModel):
  """Base for schemas that may be used as Codex/OpenAI structured-output schemas."""

  # We need this to avoid Codex complaining about us not having `additionalProperties: false`.
  model_config = ConfigDict(
    extra='forbid',
    json_schema_extra=require_all_properties,
  )
