from __future__ import annotations

from collections.abc import Iterable, Sequence

from oss20b_pro.model.backend_base import BackendInfo, ModelBackend
from oss20b_pro.model.generation_profiles import GenerationProfile


class MockBackend(ModelBackend):
    def info(self) -> BackendInfo:
        return BackendInfo(
            name="mock",
            model_path=None,
            status="ready",
            details="Development-only fake backend. It does not load or run a model.",
            is_real_model=False,
        )

    def generate_stream(
        self,
        prompt: str,
        messages: Sequence[dict[str, str]],
        profile: GenerationProfile,
    ) -> Iterable[str]:
        del prompt
        del messages
        text = f"[mock backend] This is a fake {profile.name} response for CLI testing."
        for token in text.split(" "):
            yield token + " "
