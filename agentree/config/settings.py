"""Typed application configuration, read from the environment (and `.env`)."""

import os

from claude_agent_sdk import EffortLevel
from openai_codex.generated.v2_all import Personality, ReasoningEffort
from pydantic_settings import BaseSettings, SettingsConfigDict

from agentree.types.aliases import (
  ClaudeModelAlias,
  ClaudeModelId,
  CodexModelAlias,
  CompletionClientAlias,
)


class Settings(BaseSettings):
  """Application configuration, loaded from AGENTREE_*-prefixed environment variables."""

  # The configuration is loaded from the environment variables.
  model_config = SettingsConfigDict(env_prefix='AGENTREE_', env_file='.env')

  # The completion client to use: claude or codex.
  completion_client: CompletionClientAlias = 'claude'

  # When false, skip AI completions and return empty structured responses.
  completions_enabled: bool = True

  # The model to use for the Claude Agent SDK: a short alias or a full model ID.
  claude_model: ClaudeModelAlias | ClaudeModelId = 'haiku'

  # Model the Claude client retries with on overload/capacity errors (None to disable).
  claude_fallback_model: ClaudeModelAlias | ClaudeModelId | None = None

  # Hard USD ceiling per Claude query (None for no cap).
  claude_max_budget_usd: float | None = None

  # Cap on thinking tokens per Claude query; when set, thinking switches from
  # adaptive to a fixed budget so the cap is honored (None for adaptive).
  claude_max_thinking_tokens: int | None = None

  # The model to use for the Codex SDK.
  codex_model: CodexModelAlias = 'gpt-5.6-luna'

  # When true, Codex threads are not persisted (throwaway one-shot indexing turns).
  codex_ephemeral: bool = True

  # The reasoning effort to use for the Codex client.
  codex_reasoning_effort: ReasoningEffort = ReasoningEffort.none

  # Codex service tier (e.g. 'priority', 'flex'); None uses the model's default tier.
  codex_service_tier: str | None = None

  # The reasoning effort to use for the Claude client (guides adaptive thinking depth).
  claude_reasoning_effort: EffortLevel = 'low'

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
# doesn't know about our AGENTREE_ prefix, so mirror it across explicitly.
if settings.claude_code_oauth_token:
  os.environ['CLAUDE_CODE_OAUTH_TOKEN'] = settings.claude_code_oauth_token
