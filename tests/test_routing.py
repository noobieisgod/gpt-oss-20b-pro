from __future__ import annotations

from oss20b_pro.routing.effort_router import EffortRouter
from oss20b_pro.routing.task_classifier import TaskClassifier


def test_classifier_detects_debugging() -> None:
    task = TaskClassifier().classify("I have a traceback error")
    assert task.name == "debugging"


def test_classifier_detects_coding() -> None:
    task = TaskClassifier().classify("Write a function and tests")
    assert task.name == "coding"


def test_effort_router_respects_mode() -> None:
    task = TaskClassifier().classify("I have a traceback error")
    profile = EffortRouter().select_profile(task, "quick")
    assert profile.name == "quick"


def test_effort_router_falls_back_from_unknown_mode() -> None:
    task = TaskClassifier().classify("I have a traceback error")
    profile = EffortRouter().select_profile(task, "auto")
    assert profile.name == "deep"
