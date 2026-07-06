"""Typed application configuration, read from the environment (and `.env`)."""

import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ClaudeModelAlias = Literal['haiku', 'sonnet', 'opus', 'fable']
"""Model aliases accepted by the Claude Agent SDK's `model` option."""


class Settings(BaseSettings):
  """Application configuration, loaded from PDFINDEX_*-prefixed environment variables."""

  # The configuration is loaded from the environment variables.
  model_config = SettingsConfigDict(env_prefix='PDFINDEX_', env_file='.env')

  # The model to use for the table of contents extraction.
  model: ClaudeModelAlias = 'haiku'
  # The maximum number of tokens per chunk.
  max_tokens_per_chunk: int = 20000
  # The number of pages to check for a table of contents.
  claude_code_oauth_token: str | None = None
  # The number of pages to check for a table of contents.
  top_check_page_num: int = 20


settings = Settings()

# The Claude Agent SDK only recognizes the bare CLAUDE_CODE_OAUTH_TOKEN name - it
# doesn't know about our PDFINDEX_ prefix, so mirror it across explicitly.
if settings.claude_code_oauth_token:
  os.environ['CLAUDE_CODE_OAUTH_TOKEN'] = settings.claude_code_oauth_token
