from __future__ import annotations

from oss20b_pro.cli.commands import parse_command


def test_help_command() -> None:
    assert parse_command("/help").name == "help"


def test_exit_command() -> None:
    assert parse_command("/exit").name == "exit"


def test_mode_commands() -> None:
    action = parse_command("/mode quick")
    assert action.name == "mode"
    assert action.value == "quick"


def test_debug_commands() -> None:
    action = parse_command("/debug on")
    assert action.name == "debug"
    assert action.value == "on"


def test_unknown_command() -> None:
    action = parse_command("/wat")
    assert action.name == "unknown"
    assert "Unknown command" in (action.message or "")
