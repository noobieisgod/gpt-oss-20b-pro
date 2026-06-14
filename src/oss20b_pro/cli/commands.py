from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandAction:
    name: str
    value: str | None = None
    message: str | None = None


def parse_command(text: str) -> CommandAction:
    parts = text.strip().split()
    if not parts:
        return CommandAction("unknown", message="Empty command.")

    command = parts[0].lower()
    if command == "/help":
        return CommandAction("help")
    if command == "/exit":
        return CommandAction("exit")
    if command == "/mode":
        if len(parts) == 2 and parts[1].lower() in {"quick", "normal", "deep"}:
            return CommandAction("mode", parts[1].lower())
        return CommandAction("unknown", message="Usage: /mode quick|normal|deep")
    if command == "/debug":
        if len(parts) == 2 and parts[1].lower() in {"on", "off"}:
            return CommandAction("debug", parts[1].lower())
        return CommandAction("unknown", message="Usage: /debug on|off")

    return CommandAction("unknown", message=f"Unknown command '{text}'. Type /help for commands.")
