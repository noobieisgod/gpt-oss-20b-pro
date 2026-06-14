from __future__ import annotations

from oss20b_pro.model.generation_profiles import get_profile
from oss20b_pro.model.harmony_prompt_builder import HarmonyPromptBuilder


def test_prompt_builder_orders_messages() -> None:
    builder = HarmonyPromptBuilder()
    prompt = builder.build_prompt(
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "Explain"},
        ],
        debug=False,
        profile=get_profile("normal"),
    )
    assert prompt.index("Hello") < prompt.index("Hi") < prompt.index("Explain")
    assert prompt.endswith("<|start|>assistant<|channel|>final<|message|>")


def test_prompt_builder_debug_metadata() -> None:
    builder = HarmonyPromptBuilder()
    prompt = builder.build_prompt([], debug=True, profile=get_profile("deep"))
    assert "Reasoning profile: deep" in prompt
    assert "Debug mode is enabled" in prompt
