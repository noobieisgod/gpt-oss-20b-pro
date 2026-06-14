# gpt-oss-20b-pro

`gpt-oss-20b-pro` is a local command line wrapper prototype for `gpt-oss-20b`.

v0.1 focuses on the CLI, config, backend abstraction, prompt building, routing, and clean backend errors. It does not use Ollama as a runtime.

## Install

```powershell
python -m pip install -e .[dev]
```

Optional Transformers runtime dependencies:

```powershell
python -m pip install -e .[transformers]
```

## Run

```powershell
oss chat
```

Useful development mode:

```powershell
$env:OSS20B_BACKEND = "mock"
oss chat
```

The `mock` backend streams a fake response. It is only for testing CLI flow and is not a real model backend.

## Config

Config is loaded in this order:

1. Built-in defaults
2. User config at `%USERPROFILE%\.oss20b-pro\config.toml`
3. Project config at `oss20b.toml`
4. Environment variables

Supported environment variables:

```powershell
$env:OSS20B_BACKEND = "mock"
$env:OSS20B_MODEL_PATH = "C:\path\to\transformers\model"
```

Default backend:

```toml
backend = "transformers"
model_path = "C:\\Users\\Andy\\.ollama\\models"
default_mode = "normal"
debug = false
```

## Slash Commands

```text
/help
/mode quick
/mode normal
/mode deep
/debug on
/debug off
/exit
```

## Model Path Notes

The detected local `gpt-oss:20b` install is stored under Ollama image storage. It uses manifests and blobs, including a GGUF model blob. That is not a normal Hugging Face Transformers directory.

v0.1 intentionally does not force-load Ollama storage through Transformers. If the selected backend is `transformers` and the configured path points at Ollama storage or a GGUF file, the CLI will show a clear unsupported-format error and stay usable.

A compatible Transformers model directory should contain files such as:

```text
config.json
tokenizer.json or tokenizer.model
model.safetensors or pytorch_model.bin
```

Future versions can add a GGUF or llama.cpp backend without rewriting the CLI.

## v0.1 Exclusions

No memory, RAG, web search, browser use, sub-agents, LoRA, file parsing, local API server, MCP, or Playwright.
