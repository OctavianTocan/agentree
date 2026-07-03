"""Typed application configuration, read from the environment (and `.env`)."""

import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ClaudeModelAlias = Literal["haiku", "sonnet", "opus", "fable"]
"""Model aliases accepted by the Claude Agent SDK's `model` option."""


class Settings(BaseSettings):
    """Application configuration, loaded from PDFINDEX_*-prefixed environment variables."""

    model_config = SettingsConfigDict(env_prefix="PDFINDEX_", env_file=".env")

    model: ClaudeModelAlias = "haiku"
    max_tokens_per_chunk: int = 20000
    claude_code_oauth_token: str | None = None


settings = Settings()

# The Claude Agent SDK only recognizes the bare CLAUDE_CODE_OAUTH_TOKEN name - it
# doesn't know about our PDFINDEX_ prefix, so mirror it across explicitly.
if settings.claude_code_oauth_token:
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = settings.claude_code_oauth_token
