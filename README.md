# gpt-oss-20b-pro

`gpt-oss-20b-pro` is a local command-line wrapper for `gpt-oss-20b`.

The goal is to keep the user experience simple, like chatting with one local model, while the wrapper provides a clean foundation for backends, modes, prompt formatting, routing, and future tools.

> Current status: **v0.1.2 pre-release**
>
> This is an early prototype. The wrapper can run in mock mode, validate Transformers-style model paths, and connect to an externally managed `llama.cpp` `llama-server` for real local generation.

## Features

* `oss20b chat` command-line chat interface
* Windows launcher scripts for easier local testing
* mock backend for testing the CLI without a model
* Transformers backend validation with clear unsupported-format errors
* `llama_server` backend for external `llama.cpp` OpenAI-compatible server runtime
* quick, normal, and deep generation modes
* slash commands for mode switching and debug output
* config file and environment-variable support
* clean error handling when the backend is missing or unreachable
* test suite covering config, routing, commands, backend errors, and streaming behavior

## Current limitations

* The wrapper does **not** start, install, manage, or supervise `llama-server`.
* The real model backend requires a separate `llama.cpp` server already running.
* The detected Ollama `gpt-oss:20b` storage is not loaded directly.
* The Transformers backend expects a normal Hugging Face/Transformers-compatible model directory.
* Plain `oss20b` may not work unless the Python `Scripts` directory is on PATH.
* On the current Windows/Codex setup, the bundled Python path may be needed.
* No memory, RAG, web search, browser use, sub-agents, LoRA, file parsing, MCP, Playwright, or local API server yet.

## Install

From the repo root:

```powershell
python -m pip install -e .[dev]
```

Optional Transformers dependencies:

```powershell
python -m pip install -e .[transformers]
```

If `python` is not on PATH, use the bundled Python path that works on this machine:

```powershell
C:\Users\Andy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -e .[dev]
```

## Quick start on Windows

Start `llama-server` in one PowerShell window:

```powershell
.\start-llama-server.ps1
```

Then start the wrapper in another PowerShell window:

```powershell
.\run-oss20b.ps1
```

If PowerShell blocks local scripts, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-oss20b.ps1
```

## Manual llama.cpp server startup

The wrapper expects an external OpenAI-compatible `llama-server` endpoint.

Example:

```powershell
llama-server -hf ggml-org/gpt-oss-20b-GGUF --ctx-size 32768 --jinja -ub 2048 -b 2048
```

The default wrapper server URL is:

```text
http://localhost:8080/v1
```

If the wrapper says it cannot reach `llama-server`, check that:

* `llama-server` is running in a separate terminal
* the model finished downloading and loading
* the server is listening on port `8080`
* `server_base_url` includes `/v1`

## Running the wrapper

Recommended installed command:

```powershell
oss20b chat
```

Fallback direct module command:

```powershell
python -m oss20b_pro.app chat
```

Bundled Python fallback:

```powershell
C:\Users\Andy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m oss20b_pro.app chat
```

Bundled console-script fallback:

```powershell
C:\Users\Andy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Scripts\oss20b.exe chat
```

The older `oss` command is still installed for compatibility, but PowerShell may resolve `oss` as an alias. Use `oss20b` instead.

## Mock backend

Mock mode is useful for testing the CLI without a real model:

```powershell
$env:OSS20B_BACKEND = "mock"
oss20b chat
```

The mock backend streams a fake response. It is not a real model backend.

## Real backend through llama.cpp server

Start `llama-server`, then run:

```powershell
$env:OSS20B_BACKEND = "llama_server"
oss20b chat
```

Or use the launcher:

```powershell
.\run-oss20b.ps1
```

## Config

Config is loaded in this order:

1. built-in defaults
2. user config at `%USERPROFILE%\.oss20b-pro\config.toml`
3. project config at `oss20b.toml`
4. environment variables

Supported environment variables:

```powershell
$env:OSS20B_BACKEND = "mock"
$env:OSS20B_MODEL_PATH = "C:\path\to\transformers\model"
$env:OSS20B_SERVER_BASE_URL = "http://localhost:8080/v1"
$env:OSS20B_SERVER_MODEL = "gpt-oss-20b"
$env:OSS20B_SERVER_TIMEOUT_SECONDS = "120"
```

Example config:

```toml
backend = "llama_server"
model_path = "C:\\Users\\Andy\\.ollama\\models"
default_mode = "normal"
debug = false

server_base_url = "http://localhost:8080/v1"
server_model = "gpt-oss-20b"
server_timeout_seconds = 120
context_length = 32768
```

## Slash commands

Inside `oss20b chat`:

```text
/help
/mode quick
/mode normal
/mode deep
/debug on
/debug off
/exit
```

## Backends

### `mock`

Development-only fake streaming backend.

Use it to test:

* CLI flow
* slash commands
* streaming output
* debug mode
* session behavior

### `transformers`

Validation-focused backend for future Transformers-compatible model directories.

It rejects unsupported paths clearly, including:

* Ollama model storage
* GGUF files
* missing model folders
* incomplete Transformers directories

### `llama_server`

Real local generation backend for an externally managed `llama.cpp` server.

The wrapper sends structured chat messages to:

```text
/v1/chat/completions
```

The wrapper does not manage the server process.

## Model path notes

The local `gpt-oss:20b` Ollama install is stored under Ollama image storage with manifests and blobs, including a GGUF model blob. That is not a normal Hugging Face Transformers directory.

The wrapper intentionally does not force-load Ollama storage through Transformers.

A compatible Transformers model directory should contain files such as:

```text
config.json
tokenizer.json or tokenizer.model
model.safetensors or pytorch_model.bin
```

For the current working real-runtime path, use `llama.cpp` `llama-server`.

## Tests

Run:

```powershell
python -m pytest
```

If `python` is not on PATH:

```powershell
C:\Users\Andy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest
```

Current expected result:

```text
31 passed
```

## Version history

### v0.1.2

* Added Windows launcher scripts:

  * `run-oss20b.ps1`
  * `start-llama-server.ps1`
* Improved README usage and troubleshooting instructions

### v0.1.1

* Added `llama_server` backend for external `llama.cpp` runtime
* Added `oss20b` console entry point
* Added server config fields and environment overrides
* Added streaming backend tests

### v0.1

* Added CLI wrapper foundation
* Added mock backend
* Added Transformers backend validation
* Added prompt builder abstraction
* Added routing, modes, format controller, and tests

## Roadmap

Planned future work:

* `/status` and `/backend` commands
* `/doctor` health check
* better backend diagnostics
* memory v1
* project file search
* simple RAG
* file parsing
* tool system
* web search
* browser/computer-use layer
* controlled sub-agents
* optional LoRA or adapter experiments

## License

No license has been added yet.
