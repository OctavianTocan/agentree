import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from agentree.config.settings import Settings


class _SettingsForTests(Settings):
  """Settings variant for tests that doesn't load from .env files."""

  model_config = SettingsConfigDict(env_file=None)


def test_defaults_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.delenv('AGENTREE_COMPLETION_CLIENT', raising=False)
  monkeypatch.delenv('AGENTREE_COMPLETIONS_ENABLED', raising=False)
  monkeypatch.delenv('AGENTREE_CLAUDE_MODEL', raising=False)
  monkeypatch.delenv('AGENTREE_MAX_TOKENS_PER_CHUNK', raising=False)
  monkeypatch.delenv('AGENTREE_CLAUDE_CODE_OAUTH_TOKEN', raising=False)

  settings = _SettingsForTests()

  assert settings.completion_client == 'claude'
  assert settings.completions_enabled is True
  assert settings.claude_model == 'haiku'
  assert settings.max_tokens_per_chunk == 20000
  assert settings.claude_code_oauth_token is None


def test_reads_completions_enabled_as_bool(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setenv('AGENTREE_COMPLETIONS_ENABLED', '0')

  settings = _SettingsForTests()

  assert settings.completions_enabled is False


def test_rejects_invalid_claude_model_alias(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setenv('AGENTREE_CLAUDE_MODEL', 'not-a-real-model')

  with pytest.raises(ValidationError):
    _SettingsForTests()


def test_reads_max_tokens_per_chunk_as_int(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setenv('AGENTREE_MAX_TOKENS_PER_CHUNK', '5000')

  settings = _SettingsForTests()

  assert settings.max_tokens_per_chunk == 5000
