from __future__ import annotations

from pathlib import Path

import pytest

from oss20b_pro.config import AppConfig, load_config
from oss20b_pro.model.backend_base import build_backend
from oss20b_pro.model.llama_server_backend import LlamaServerBackend
from oss20b_pro.model.mock_backend import MockBackend
from oss20b_pro.model.transformers_backend import TransformersBackend
from oss20b_pro.utils.errors import (
    IncompleteModelDirectoryError,
    ModelPathNotFoundError,
    UnsupportedModelFormatError,
)


def test_backend_selection_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    config = load_config(cwd=tmp_path, env={"OSS20B_BACKEND": "mock"})
    backend = build_backend(config)
    assert isinstance(backend, MockBackend)


def test_llama_server_backend_selection_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    config = load_config(cwd=tmp_path, env={"OSS20B_BACKEND": "llama_server"})
    backend = build_backend(config)
    assert isinstance(backend, LlamaServerBackend)


def test_mock_backend_streaming() -> None:
    backend = MockBackend()
    chunks = list(backend.generate_stream("prompt", [], profile=__import_profile()))
    assert "".join(chunks).startswith("[mock backend]")
    assert backend.info().is_real_model is False


def test_missing_model_path() -> None:
    with pytest.raises(ModelPathNotFoundError):
        TransformersBackend("Z:\\definitely\\missing\\model")


def test_ollama_storage_rejected(tmp_path: Path) -> None:
    (tmp_path / "blobs").mkdir()
    (tmp_path / "manifests").mkdir()
    with pytest.raises(UnsupportedModelFormatError) as exc_info:
        TransformersBackend(str(tmp_path))
    assert "Detected Ollama model storage" in str(exc_info.value)


def test_gguf_file_rejected(tmp_path: Path) -> None:
    gguf = tmp_path / "model.gguf"
    gguf.write_bytes(b"GGUF")
    with pytest.raises(UnsupportedModelFormatError):
        TransformersBackend(str(gguf))


def test_incomplete_transformers_directory_rejected(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    with pytest.raises(IncompleteModelDirectoryError):
        TransformersBackend(str(tmp_path))


def test_valid_looking_transformers_directory_validates(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "tokenizer.json").write_text("{}", encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"fake")
    backend = TransformersBackend(str(tmp_path))
    assert backend.info().status == "validated"


def __import_profile():
    from oss20b_pro.model.generation_profiles import get_profile

    return get_profile("quick")
