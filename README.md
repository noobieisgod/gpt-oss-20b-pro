# gpt-oss-20b-pro

`gpt-oss-20b-pro` is a local command line wrapper prototype for `gpt-oss-20b`.

v0.1 focuses on the CLI, config, backend abstraction, prompt building, routing, and clean backend errors. v0.1.1 adds an optional client backend for an externally managed llama.cpp `llama-server`.

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
oss20b chat
```

Fallback direct module command:

```powershell
python -m oss20b_pro.app chat
```

The older `oss` console script is still installed for compatibility, but PowerShell may resolve `oss` as an alias. Use `oss20b` as the recommended command.

Useful development mode:

```powershell
$env:OSS20B_BACKEND = "mock"
oss20b chat
```

The `mock` backend streams a fake response. It is only for testing CLI flow and is not a real model backend.

Real local runtime via llama.cpp server:

```powershell
$env:OSS20B_BACKEND = "llama_server"
oss20b chat
```

The wrapper does not install, start, manage, or supervise `llama-server`. Start it yourself before using the `llama_server` backend.

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
$env:OSS20B_SERVER_BASE_URL = "http://localhost:8080/v1"
$env:OSS20B_SERVER_MODEL = "gpt-oss-20b"
$env:OSS20B_SERVER_TIMEOUT_SECONDS = "120"
```

Default backend:

```toml
backend = "transformers"
model_path = "C:\\Users\\Andy\\.ollama\\models"
default_mode = "normal"
debug = false
server_base_url = "http://localhost:8080/v1"
server_model = "gpt-oss-20b"
server_timeout_seconds = 120
context_length = 32768
```

For a local llama.cpp server backend:

```toml
backend = "llama_server"
server_base_url = "http://localhost:8080/v1"
server_model = "gpt-oss-20b"
server_timeout_seconds = 120
context_length = 32768
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

## llama.cpp llama-server

v0.1.1 can connect to an already running OpenAI-compatible `llama-server`.

Example manual startup:

```powershell
llama-server -hf ggml-org/gpt-oss-20b-GGUF --ctx-size 32768 --jinja -ub 2048 -b 2048
```

Then run the wrapper:

```powershell
$env:OSS20B_BACKEND = "llama_server"
oss20b chat
```

The configured `server_base_url` should include `/v1`, for example `http://localhost:8080/v1`.

If you installed with the bundled Codex Python runtime and its Scripts directory is not on PATH, the full console script path is:

```powershell
C:\Users\Andy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Scripts\oss20b.exe chat
```

## v0.1 Exclusions

No memory, RAG, web search, browser use, sub-agents, LoRA, file parsing, local API server, MCP, or Playwright.
