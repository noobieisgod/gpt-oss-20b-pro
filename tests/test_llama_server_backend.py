from __future__ import annotations

import socket
from collections.abc import Iterable
from urllib import error, request

import pytest

from oss20b_pro.model.generation_profiles import get_profile
from oss20b_pro.model.llama_server_backend import LlamaServerBackend
from oss20b_pro.utils.errors import (
    InvalidBackendResponseError,
    MalformedStreamEventError,
    ServerResponseStatusError,
    ServerTimeoutError,
    ServerUnreachableError,
)


class FakeResponse:
    def __init__(self, lines: Iterable[bytes], status: int = 200) -> None:
        self._lines = list(lines)
        self.status = status

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def __iter__(self):
        return iter(self._lines)


def test_llama_server_streaming_yields_text() -> None:
    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=lambda req, timeout: FakeResponse(
            [
                b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
                b'data: {"choices":[{"delta":{"content":" world"}}]}\n\n',
                b"data: [DONE]\n\n",
            ]
        ),
    )

    chunks = list(backend.generate_stream("ignored", [{"role": "user", "content": "Hi"}], get_profile("quick")))

    assert "".join(chunks) == "Hello world"


def test_llama_server_unreachable_error() -> None:
    def raise_unreachable(req: request.Request, timeout: float):
        raise error.URLError("connection refused")

    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=raise_unreachable,
    )

    with pytest.raises(ServerUnreachableError):
        list(backend.generate_stream("ignored", [], get_profile("quick")))


def test_llama_server_timeout_error() -> None:
    def raise_timeout(req: request.Request, timeout: float):
        raise socket.timeout("timed out")

    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=raise_timeout,
    )

    with pytest.raises(ServerTimeoutError):
        list(backend.generate_stream("ignored", [], get_profile("quick")))


def test_llama_server_non_2xx_error() -> None:
    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=lambda req, timeout: FakeResponse([], status=500),
    )

    with pytest.raises(ServerResponseStatusError):
        list(backend.generate_stream("ignored", [], get_profile("quick")))


def test_llama_server_invalid_response_error() -> None:
    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=lambda req, timeout: FakeResponse([b'data: {"not_choices":[]}\n\n']),
    )

    with pytest.raises(InvalidBackendResponseError):
        list(backend.generate_stream("ignored", [], get_profile("quick")))


def test_llama_server_malformed_json_stream_event_error() -> None:
    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=lambda req, timeout: FakeResponse([b"data: {bad json}\n\n"]),
    )

    with pytest.raises(MalformedStreamEventError):
        list(backend.generate_stream("ignored", [], get_profile("quick")))


def test_llama_server_malformed_stream_event_error() -> None:
    backend = LlamaServerBackend(
        base_url="http://localhost:8080/v1",
        model="gpt-oss-20b",
        timeout_seconds=5,
        urlopen_func=lambda req, timeout: FakeResponse([b"event: message\n\n"]),
    )

    with pytest.raises(MalformedStreamEventError):
        list(backend.generate_stream("ignored", [], get_profile("quick")))
