from __future__ import annotations

from collections.abc import Sequence

from oss20b_pro.model.generation_profiles import GenerationProfile


class HarmonyPromptBuilder:
    def build_prompt(
        self,
        messages: Sequence[dict[str, str]],
        *,
        debug: bool,
        profile: GenerationProfile,
    ) -> str:
        parts = [
            "<|start|>system<|message|>",
            "You are a local assistant running through the gpt-oss-20b-pro CLI wrapper.",
            f"\nReasoning profile: {profile.name}",
        ]
        if debug:
            parts.append("\nDebug mode is enabled. Include concise internal routing details only when useful.")
        parts.append("<|end|>")

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role not in {"user", "assistant"}:
                continue
            channel = "<|channel|>final" if role == "assistant" else ""
            parts.append(f"<|start|>{role}{channel}<|message|>{content}<|end|>")

        parts.append("<|start|>assistant<|channel|>final<|message|>")
        return "".join(parts)
