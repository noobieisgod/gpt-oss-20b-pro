from __future__ import annotations

from oss20b_pro.model.generation_profiles import GenerationProfile, get_profile
from oss20b_pro.routing.task_classifier import TaskType

DEEP_TASKS = {"architecture", "debugging", "long_context"}
NORMAL_TASKS = {"coding", "formatting"}


class EffortRouter:
    def select_profile(self, task: TaskType, mode: str) -> GenerationProfile:
        if mode in {"quick", "normal", "deep"}:
            selected = mode
        elif task.name in DEEP_TASKS:
            selected = "deep"
        elif task.name in NORMAL_TASKS:
            selected = "normal"
        else:
            selected = "quick"
        return get_profile(selected)
