import pytest
from pydantic import ValidationError

from PDFindex.settings import Settings


def test_defaults_when_unset(monkeypatch):
    monkeypatch.delenv("PDFINDEX_MODEL", raising=False)
    monkeypatch.delenv("PDFINDEX_MAX_TOKENS_PER_CHUNK", raising=False)
    monkeypatch.delenv("PDFINDEX_CLAUDE_CODE_OAUTH_TOKEN", raising=False)

    settings = Settings(_env_file=None)

    assert settings.model == "haiku"
    assert settings.max_tokens_per_chunk == 20000
    assert settings.claude_code_oauth_token is None


def test_rejects_invalid_model_alias(monkeypatch):
    monkeypatch.setenv("PDFINDEX_MODEL", "not-a-real-model")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_reads_max_tokens_per_chunk_as_int(monkeypatch):
    monkeypatch.setenv("PDFINDEX_MAX_TOKENS_PER_CHUNK", "5000")

    settings = Settings(_env_file=None)

    assert settings.max_tokens_per_chunk == 5000
