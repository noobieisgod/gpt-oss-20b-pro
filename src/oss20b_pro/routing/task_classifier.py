from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskType:
    name: str


class TaskClassifier:
    def classify(self, text: str) -> TaskType:
        lowered = text.lower()
        if len(text) > 800:
            return TaskType("long_context")
        if any(word in lowered for word in ("debug", "traceback", "exception", "error", "failing")):
            return TaskType("debugging")
        if any(word in lowered for word in ("code", "function", "class", "test", "refactor")):
            return TaskType("coding")
        if any(word in lowered for word in ("architecture", "design", "roadmap", "plan")):
            return TaskType("architecture")
        if any(word in lowered for word in ("json", "table", "format")):
            return TaskType("formatting")
        return TaskType("general")
