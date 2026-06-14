from __future__ import annotations

import importlib.util
from collections.abc import Iterable, Sequence
from pathlib import Path

from oss20b_pro.model.backend_base import BackendInfo, ModelBackend
from oss20b_pro.model.generation_profiles import GenerationProfile
from oss20b_pro.utils.errors import (
    IncompleteModelDirectoryError,
    MissingBackendDependencyError,
    ModelLoadError,
    ModelPathNotFoundError,
    UnsupportedModelFormatError,
)

TOKENIZER_FILES = {"tokenizer.json", "tokenizer.model", "vocab.json"}
WEIGHT_SUFFIXES = {".safetensors", ".bin"}


class TransformersBackend(ModelBackend):
    def __init__(self, model_path: str) -> None:
        self.model_path = Path(model_path)
        self._tokenizer = None
        self._model = None
        validate_transformers_model_path(self.model_path)

    def info(self) -> BackendInfo:
        return BackendInfo(
            name="transformers",
            model_path=str(self.model_path),
            status="validated",
            details="Transformers backend path has passed local format checks.",
            is_real_model=True,
        )

    def generate_stream(
        self,
        prompt: str,
        messages: Sequence[dict[str, str]],
        profile: GenerationProfile,
    ) -> Iterable[str]:
        del messages
        self._ensure_dependencies()
        self._ensure_loaded()

        inputs = self._tokenizer(prompt, return_tensors="pt")
        output = self._model.generate(
            **inputs,
            max_new_tokens=profile.max_new_tokens,
            temperature=profile.temperature,
            top_p=profile.top_p,
            do_sample=profile.temperature > 0,
        )
        decoded = self._tokenizer.decode(output[0], skip_special_tokens=True)
        response = decoded[len(prompt) :] if decoded.startswith(prompt) else decoded
        for token in response.split(" "):
            if token:
                yield token + " "

    def _ensure_dependencies(self) -> None:
        missing = [
            package
            for package in ("transformers", "torch")
            if importlib.util.find_spec(package) is None
        ]
        if missing:
            joined = ", ".join(missing)
            raise MissingBackendDependencyError(
                "The Transformers backend requires optional dependencies "
                f"that are not installed: {joined}. Install with: python -m pip install -e .[transformers]"
            )

    def _ensure_loaded(self) -> None:
        if self._tokenizer is not None and self._model is not None:
            return
        self._ensure_dependencies()
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            self._model = AutoModelForCausalLM.from_pretrained(str(self.model_path))
        except Exception as exc:
            raise ModelLoadError(f"Failed to load Transformers model at {self.model_path}: {exc}") from exc


def validate_transformers_model_path(model_path: Path) -> None:
    if not model_path.exists():
        raise ModelPathNotFoundError(
            f"Model path does not exist: {model_path}. Set OSS20B_MODEL_PATH or model_path in config."
        )

    if model_path.is_file():
        if model_path.suffix.lower() == ".gguf":
            raise UnsupportedModelFormatError(_gguf_message(model_path))
        raise UnsupportedModelFormatError(
            f"Expected a Transformers model directory, but got a file: {model_path}"
        )

    if (model_path / "blobs").is_dir() and (model_path / "manifests").is_dir():
        raise UnsupportedModelFormatError(_ollama_storage_message(model_path))

    children = {child.name for child in model_path.iterdir()}
    if "config.json" not in children:
        raise IncompleteModelDirectoryError(
            f"Transformers model directory is missing config.json: {model_path}"
        )
    if not TOKENIZER_FILES.intersection(children):
        raise IncompleteModelDirectoryError(
            f"Transformers model directory is missing tokenizer files: {model_path}"
        )
    if not any(child.suffix.lower() in WEIGHT_SUFFIXES for child in model_path.iterdir()):
        raise IncompleteModelDirectoryError(
            f"Transformers model directory is missing .safetensors or .bin weights: {model_path}"
        )


def _ollama_storage_message(model_path: Path) -> str:
    return (
        f"Detected Ollama model storage at {model_path}. "
        "This contains Ollama manifests and blobs, not a normal Hugging Face Transformers model directory. "
        "Transformers cannot load this storage path directly. "
        "Ollama is not used as the runtime for this project. "
        "Set OSS20B_MODEL_PATH or model_path in config to a Transformers-compatible gpt-oss-20b directory, "
        "or use OSS20B_BACKEND=mock for CLI testing."
    )


def _gguf_message(model_path: Path) -> str:
    return (
        f"Detected GGUF model file at {model_path}. "
        "The v0.1 Transformers backend expects a Hugging Face Transformers directory, not GGUF. "
        "A GGUF or llama.cpp backend can be added later without changing the CLI."
    )
