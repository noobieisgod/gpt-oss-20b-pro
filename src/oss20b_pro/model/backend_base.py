from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from oss20b_pro.config import AppConfig
from oss20b_pro.model.generation_profiles import GenerationProfile
from oss20b_pro.utils.errors import ConfigError


@dataclass(frozen=True)
class BackendInfo:
    name: str
    model_path: str | None
    status: str
    details: str
    is_real_model: bool


class ModelBackend(ABC):
    @abstractmethod
    def info(self) -> BackendInfo:
        raise NotImplementedError

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        messages: Sequence[dict[str, str]],
        profile: GenerationProfile,
    ) -> Iterable[str]:
        raise NotImplementedError


def build_backend(config: AppConfig) -> ModelBackend:
    if config.backend == "mock":
        from oss20b_pro.model.mock_backend import MockBackend

        return MockBackend()
    if config.backend == "transformers":
        from oss20b_pro.model.transformers_backend import TransformersBackend

        return TransformersBackend(config.model_path)
    raise ConfigError(f"Unsupported backend '{config.backend}'.")
