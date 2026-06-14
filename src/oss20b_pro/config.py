from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from oss20b_pro.utils.errors import ConfigError

SUPPORTED_BACKENDS = {"transformers", "mock"}
SUPPORTED_MODES = {"quick", "normal", "deep"}


@dataclass(frozen=True)
class AppConfig:
    backend: str = "transformers"
    model_path: str = r"C:\Users\Andy\.ollama\models"
    default_mode: str = "normal"
    debug: bool = False


def user_config_path() -> Path:
    return Path.home() / ".oss20b-pro" / "config.toml"


def project_config_path(cwd: Path | None = None) -> Path:
    return (cwd or Path.cwd()) / "oss20b.toml"


def load_config(
    *,
    explicit_config_path: str | None = None,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> AppConfig:
    values: dict[str, Any] = {
        "backend": AppConfig.backend,
        "model_path": AppConfig.model_path,
        "default_mode": AppConfig.default_mode,
        "debug": AppConfig.debug,
    }

    if explicit_config_path:
        values.update(_read_toml(Path(explicit_config_path)))
    else:
        user_path = user_config_path()
        project_path = project_config_path(cwd)
        if user_path.exists():
            values.update(_read_toml(user_path))
        if project_path.exists():
            values.update(_read_toml(project_path))

    current_env = os.environ if env is None else env
    if current_env.get("OSS20B_BACKEND"):
        values["backend"] = current_env["OSS20B_BACKEND"]
    if current_env.get("OSS20B_MODEL_PATH"):
        values["model_path"] = current_env["OSS20B_MODEL_PATH"]

    return _coerce_config(values)


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            loaded = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML config at {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Could not read config at {path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ConfigError(f"Config at {path} must contain a TOML table.")
    return loaded


def _coerce_config(values: Mapping[str, Any]) -> AppConfig:
    backend = str(values.get("backend", AppConfig.backend)).strip().lower()
    if backend not in SUPPORTED_BACKENDS:
        supported = ", ".join(sorted(SUPPORTED_BACKENDS))
        raise ConfigError(f"Unsupported backend '{backend}'. Supported backends: {supported}.")

    default_mode = str(values.get("default_mode", AppConfig.default_mode)).strip().lower()
    if default_mode not in SUPPORTED_MODES:
        supported = ", ".join(sorted(SUPPORTED_MODES))
        raise ConfigError(f"Unsupported default_mode '{default_mode}'. Supported modes: {supported}.")

    model_path = str(values.get("model_path", AppConfig.model_path)).strip()
    if not model_path:
        raise ConfigError("model_path cannot be empty.")

    debug_value = values.get("debug", AppConfig.debug)
    if isinstance(debug_value, bool):
        debug = debug_value
    elif isinstance(debug_value, str):
        debug = debug_value.strip().lower() in {"1", "true", "yes", "on"}
    else:
        raise ConfigError("debug must be a boolean.")

    return AppConfig(
        backend=backend,
        model_path=model_path,
        default_mode=default_mode,
        debug=debug,
    )
