from __future__ import annotations

from oss20b_pro.checking.format_controller import FormatController
from oss20b_pro.cli.commands import CommandAction, parse_command
from oss20b_pro.cli.session import ChatSession
from oss20b_pro.cli.streaming import print_stream
from oss20b_pro.config import AppConfig
from oss20b_pro.model.backend_base import build_backend
from oss20b_pro.model.harmony_prompt_builder import HarmonyPromptBuilder
from oss20b_pro.routing.effort_router import EffortRouter
from oss20b_pro.routing.task_classifier import TaskClassifier
from oss20b_pro.utils.errors import Oss20bError


def run_chat(config: AppConfig) -> int:
    session = ChatSession(mode=config.default_mode, debug=config.debug)
    classifier = TaskClassifier()
    effort_router = EffortRouter()
    prompt_builder = HarmonyPromptBuilder()
    format_controller = FormatController()
    backend = None

    print("oss20b chat v0.1")
    print("Type /help for commands or /exit to quit.")

    while True:
        try:
            raw_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            print("Exiting.")
            return 0

        user_input = raw_input.strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            action = parse_command(user_input)
            if action.name == "exit":
                print("Exiting.")
                return 0
            _handle_command(action, session, config, backend)
            continue

        task = classifier.classify(user_input)
        profile = effort_router.select_profile(task, session.mode)
        session.add_user_message(user_input)

        if session.debug:
            print(f"[debug] task={task.name} mode={session.mode} profile={profile.name}")
            if backend is not None:
                info = backend.info()
                print(
                    f"[debug] backend={info.name} status={info.status} "
                    f"model_path={info.model_path} details={info.details}"
                )
            else:
                print(f"[debug] backend={config.backend} status=not_initialized {_configured_backend_target(config)}")

        try:
            if backend is None:
                backend = build_backend(config)
            prompt = prompt_builder.build_prompt(
                session.messages,
                debug=session.debug,
                profile=profile,
            )
            response_chunks = backend.generate_stream(prompt, session.messages, profile)
            response_text = print_stream(response_chunks)
            response_text = format_controller.apply(response_text)
            session.add_assistant_message(response_text)
        except Oss20bError as exc:
            print(_format_error(exc, session.debug))


def _handle_command(
    action: CommandAction,
    session: ChatSession,
    config: AppConfig,
    backend: object | None,
) -> None:
    if action.name == "help":
        print(HELP_TEXT)
        return

    if action.name == "mode":
        session.mode = action.value or session.mode
        print(f"Mode set to {session.mode}.")
        return

    if action.name == "debug":
        session.debug = action.value == "on"
        print(f"Debug {'on' if session.debug else 'off'}.")
        if session.debug:
            print(f"[debug] configured_backend={config.backend} {_configured_backend_target(config)}")
            if backend is not None and hasattr(backend, "info"):
                info = backend.info()
                print(f"[debug] backend={info.name} status={info.status} details={info.details}")
        return

    print(action.message or "Unknown command. Type /help for commands.")


def _format_error(error: Oss20bError, debug: bool) -> str:
    message = f"Backend error: {error}"
    if debug and error.__cause__ is not None:
        message += f"\n[debug] cause={error.__cause__!r}"
    return message


def _configured_backend_target(config: AppConfig) -> str:
    if config.backend == "llama_server":
        return f"server_url={config.server_base_url} server_model={config.server_model}"
    return f"model_path={config.model_path}"


HELP_TEXT = """Commands:
  /help
  /mode quick
  /mode normal
  /mode deep
  /debug on
  /debug off
  /exit
"""
