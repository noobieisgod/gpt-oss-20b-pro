from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationProfile:
    name: str
    max_new_tokens: int
    temperature: float
    top_p: float


PROFILES: dict[str, GenerationProfile] = {
    "quick": GenerationProfile("quick", max_new_tokens=256, temperature=0.2, top_p=0.9),
    "normal": GenerationProfile("normal", max_new_tokens=768, temperature=0.4, top_p=0.95),
    "deep": GenerationProfile("deep", max_new_tokens=1536, temperature=0.5, top_p=0.95),
}


def get_profile(name: str) -> GenerationProfile:
    return PROFILES.get(name, PROFILES["normal"])
