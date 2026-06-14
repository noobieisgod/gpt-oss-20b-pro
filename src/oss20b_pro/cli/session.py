from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChatSession:
    mode: str = "normal"
    debug: bool = False
    messages: list[dict[str, str]] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})
