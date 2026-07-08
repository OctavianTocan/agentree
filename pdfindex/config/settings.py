"""Typed application configuration, read from the environment (and `.env`)."""

import os

from openai_codex.generated.v2_all import Personality, ReasoningEffort
from pydantic_settings import BaseSettings, SettingsConfigDict

from pdfindex.types.aliases import (
  ClaudeModelAlias,
  CodexModelAlias,
  CompletionClientAlias,
)


class Settings(BaseSettings):
  """Application configuration, loaded from PDFINDEX_*-prefixed environment variables."""

  # The configuration is loaded from the environment variables.
  model_config = SettingsConfigDict(env_prefix='PDFINDEX_', env_file='.env')

  # The completion client to use: claude or codex.
  completion_client: CompletionClientAlias = 'claude'

  # The model to use for the Claude Agent SDK. Defaults to haiku.
  claude_model: ClaudeModelAlias = 'haiku'

  # The model to use for the Codex SDK.
  codex_model: CodexModelAlias = 'gpt-5.5'

  # The reasoning effort to use for the Codex client.
  codex_reasoning_effort: ReasoningEffort = ReasoningEffort.medium

  # The personality to use for the Codex client.
  personality: Personality = Personality.pragmatic

  # The maximum number of tokens per chunk.
  max_tokens_per_chunk: int = 20000

  # OAuth token from `claude setup-token`.
  claude_code_oauth_token: str | None = None

  # How many leading pages to scan for an embedded table of contents.
  top_check_page_num: int = 20


settings = Settings()

# The Claude Agent SDK only recognizes the bare CLAUDE_CODE_OAUTH_TOKEN name - it
# doesn't know about our PDFINDEX_ prefix, so mirror it across explicitly.
if settings.claude_code_oauth_token:
  os.environ['CLAUDE_CODE_OAUTH_TOKEN'] = settings.claude_code_oauth_token
