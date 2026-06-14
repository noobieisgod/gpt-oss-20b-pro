from __future__ import annotations

from pathlib import Path

import pytest

from oss20b_pro.config import AppConfig, load_config
from oss20b_pro.utils.errors import ConfigError


def test_config_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    config = load_config(cwd=tmp_path, env={})
    assert config.backend == "transformers"
    assert config.model_path == AppConfig.model_path
    assert config.default_mode == "normal"
    assert config.server_base_url == "http://localhost:8080/v1"
    assert config.server_model == "gpt-oss-20b"
    assert config.server_timeout_seconds == 120
    assert config.context_length == 32768


def test_env_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    config = load_config(
        cwd=tmp_path,
        env={
            "OSS20B_BACKEND": "llama_server",
            "OSS20B_MODEL_PATH": "C:\\models\\gpt-oss",
            "OSS20B_SERVER_BASE_URL": "http://127.0.0.1:9000/v1/",
            "OSS20B_SERVER_MODEL": "local-gpt-oss",
            "OSS20B_SERVER_TIMEOUT_SECONDS": "10",
        },
    )
    assert config.backend == "llama_server"
    assert config.model_path == "C:\\models\\gpt-oss"
    assert config.server_base_url == "http://127.0.0.1:9000/v1"
    assert config.server_model == "local-gpt-oss"
    assert config.server_timeout_seconds == 10


def test_project_config_overrides_user_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home = tmp_path / "home"
    user_dir = home / ".oss20b-pro"
    user_dir.mkdir(parents=True)
    (user_dir / "config.toml").write_text('backend = "mock"\n', encoding="utf-8")
    (tmp_path / "oss20b.toml").write_text('backend = "transformers"\n', encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: home)

    config = load_config(cwd=tmp_path, env={})
    assert config.backend == "transformers"


def test_invalid_toml_raises_config_error(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.toml"
    config_path.write_text("backend = [", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(explicit_config_path=str(config_path), env={})


def test_invalid_timeout_raises_config_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")

    with pytest.raises(ConfigError):
        load_config(cwd=tmp_path, env={"OSS20B_SERVER_TIMEOUT_SECONDS": "0"})
