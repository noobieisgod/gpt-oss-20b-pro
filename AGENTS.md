# Project Instructions for Codex

This project is `gpt-oss-20b-pro`, a local command-line wrapper prototype for `gpt-oss-20b`.

## Plan-First Workflow

- Always inspect the relevant files before editing.
- Always write an implementation plan before modifying code.
- For large, risky, or multi-file changes, stop after the plan and wait for approval.
- For small safe changes, write the plan first, then proceed.
- Never edit code immediately without first stating the plan.

## Current v0.1 Scope

Keep v0.1 focused on:

- CLI chat experience.
- Config loading.
- Backend abstraction.
- Mock backend.
- Transformers backend validation.
- Harmony prompt builder abstraction.
- Routing.
- Quick, normal, and deep modes.
- Basic format controller.
- Tests.

Do not add these unless explicitly requested:

- Memory.
- RAG.
- Web search.
- Browser use.
- Sub-agents.
- LoRA.
- File parsing.
- Local API server.
- MCP.
- Playwright.

## Product and UX Rules

- Preserve the normal model-like CLI experience.
- Hide internal routing unless debug mode is enabled.
- Keep the backend modular so future GGUF, llama.cpp, or Transformers backends can be added cleanly.
- Do not force-load Ollama storage through Transformers.
- Use clear typed errors for backend failures.
- Keep the `mock` backend clearly labeled as development-only and not a real model backend.

## Engineering Rules

- Prefer readable, well-tested code over clever code.
- Use type hints where practical.
- Use standard Python logging.
- Add or update tests when behavior changes.
- Run `python -m pytest` after code changes when practical.
- If `python` is unavailable on PATH in this environment, use the bundled Codex Python runtime.

## Closeout Requirements

At the end of each implementation pass, summarize:

- Files changed.
- Tests run and results.
- Known limitations or follow-up work.
