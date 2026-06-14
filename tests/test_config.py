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


def test_env_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    config = load_config(
        cwd=tmp_path,
        env={"OSS20B_BACKEND": "mock", "OSS20B_MODEL_PATH": "C:\\models\\gpt-oss"},
    )
    assert config.backend == "mock"
    assert config.model_path == "C:\\models\\gpt-oss"


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
