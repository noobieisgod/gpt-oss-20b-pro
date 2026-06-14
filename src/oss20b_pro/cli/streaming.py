from __future__ import annotations

from collections.abc import Iterable


def print_stream(chunks: Iterable[str]) -> str:
    collected: list[str] = []
    print("Assistant: ", end="", flush=True)
    for chunk in chunks:
        print(chunk, end="", flush=True)
        collected.append(chunk)
    print()
    return "".join(collected)
