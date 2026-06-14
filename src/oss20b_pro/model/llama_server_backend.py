from __future__ import annotations

import json
import socket
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from oss20b_pro.model.backend_base import BackendInfo, ModelBackend
from oss20b_pro.model.generation_profiles import GenerationProfile
from oss20b_pro.utils.errors import (
    InvalidBackendResponseError,
    MalformedStreamEventError,
    ServerResponseStatusError,
    ServerTimeoutError,
    ServerUnreachableError,
)


UrlOpen = Callable[[request.Request, float], Any]


@dataclass(frozen=True)
class LlamaServerSettings:
    base_url: str
    model: str
    timeout_seconds: int


class LlamaServerBackend(ModelBackend):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: int,
        urlopen_func: UrlOpen | None = None,
    ) -> None:
        self.settings = LlamaServerSettings(
            base_url=base_url.rstrip("/"),
            model=model,
            timeout_seconds=timeout_seconds,
        )
        self._urlopen = urlopen_func or request.urlopen

    def info(self) -> BackendInfo:
        return BackendInfo(
            name="llama_server",
            model_path=None,
            status="configured",
            details=f"server_url={self.settings.base_url} model={self.settings.model}",
            is_real_model=True,
        )

    def generate_stream(
        self,
        prompt: str,
        messages: Sequence[dict[str, str]],
        profile: GenerationProfile,
    ) -> Iterable[str]:
        del prompt
        payload = {
            "model": self.settings.model,
            "messages": _chat_messages(messages),
            "stream": True,
            "max_tokens": profile.max_new_tokens,
            "temperature": profile.temperature,
            "top_p": profile.top_p,
        }
        request_body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.settings.base_url}/chat/completions",
            data=request_body,
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
            method="POST",
        )

        try:
            with self._urlopen(req, timeout=float(self.settings.timeout_seconds)) as response:
                status = int(getattr(response, "status", 200))
                if status < 200 or status >= 300:
                    raise ServerResponseStatusError(
                        f"llama-server returned HTTP {status} from {self.settings.base_url}."
                    )
                yield from _iter_stream_chunks(response)
        except ServerResponseStatusError:
            raise
        except error.HTTPError as exc:
            body = _safe_read_error_body(exc)
            message = f"llama-server returned HTTP {exc.code} from {self.settings.base_url}."
            if body:
                message += f" Response body: {body}"
            raise ServerResponseStatusError(message) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise ServerTimeoutError(
                f"Timed out after {self.settings.timeout_seconds} seconds connecting to llama-server at "
                f"{self.settings.base_url}."
            ) from exc
        except error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, (TimeoutError, socket.timeout)):
                raise ServerTimeoutError(
                    f"Timed out after {self.settings.timeout_seconds} seconds connecting to llama-server at "
                    f"{self.settings.base_url}."
                ) from exc
            raise ServerUnreachableError(
                f"Could not reach llama-server at {self.settings.base_url}. "
                "Start llama-server manually or update server_base_url."
            ) from exc


def _chat_messages(messages: Sequence[dict[str, str]]) -> list[dict[str, str]]:
    prepared: list[dict[str, str]] = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant", "system"} and isinstance(content, str):
            prepared.append({"role": role, "content": content})
    return prepared


def _iter_stream_chunks(response: Iterable[bytes]) -> Iterable[str]:
    saw_event = False
    for raw_line in response:
        line = raw_line.decode("utf-8").strip()
        if not line or line.startswith(":"):
            continue
        if not line.startswith("data:"):
            raise MalformedStreamEventError(f"Malformed stream event from llama-server: {line}")

        event_data = line.removeprefix("data:").strip()
        if event_data == "[DONE]":
            return

        saw_event = True
        try:
            payload = json.loads(event_data)
        except json.JSONDecodeError as exc:
            raise MalformedStreamEventError(f"Malformed JSON stream event from llama-server: {event_data}") from exc

        content = _extract_content_delta(payload)
        if content:
            yield content

    if not saw_event:
        raise InvalidBackendResponseError("llama-server returned an empty streaming response.")


def _extract_content_delta(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        raise InvalidBackendResponseError("llama-server stream event must be a JSON object.")

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise InvalidBackendResponseError("llama-server stream event is missing choices.")

    choice = choices[0]
    if not isinstance(choice, dict):
        raise InvalidBackendResponseError("llama-server stream choice must be an object.")

    delta = choice.get("delta")
    if not isinstance(delta, dict):
        raise InvalidBackendResponseError("llama-server stream choice is missing delta.")

    content = delta.get("content")
    if content is None:
        return None
    if not isinstance(content, str):
        raise InvalidBackendResponseError("llama-server stream content must be a string.")
    return content


def _safe_read_error_body(exc: error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="replace").strip()
    except Exception:
        return ""
