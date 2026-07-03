import pytest
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from PDFindex.settings import ClaudeModelAlias


class _SettingsForTests(BaseSettings):
    """Settings variant for tests that doesn't load from .env files."""

    model_config = SettingsConfigDict(env_prefix="PDFINDEX_")

    model: ClaudeModelAlias = "haiku"
    max_tokens_per_chunk: int = 20000
    claude_code_oauth_token: str | None = None


def test_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("PDFINDEX_MODEL", raising=False)
    monkeypatch.delenv("PDFINDEX_MAX_TOKENS_PER_CHUNK", raising=False)
    monkeypatch.delenv("PDFINDEX_CLAUDE_CODE_OAUTH_TOKEN", raising=False)

    settings = _SettingsForTests()

    assert settings.model == "haiku"
    assert settings.max_tokens_per_chunk == 20000
    assert settings.claude_code_oauth_token is None


def test_rejects_invalid_model_alias(monkeypatch):
    monkeypatch.setenv("PDFINDEX_MODEL", "not-a-real-model")

    with pytest.raises(ValidationError):
        _SettingsForTests()


def test_reads_max_tokens_per_chunk_as_int(monkeypatch):
    monkeypatch.setenv("PDFINDEX_MAX_TOKENS_PER_CHUNK", "5000")

    settings = _SettingsForTests()

    assert settings.max_tokens_per_chunk == 5000
