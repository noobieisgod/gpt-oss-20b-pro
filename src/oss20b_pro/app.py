from __future__ import annotations

import argparse
from collections.abc import Sequence

from oss20b_pro.cli.chat import run_chat
from oss20b_pro.config import load_config
from oss20b_pro.logging_setup import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oss20b", description="Local gpt-oss-20b wrapper.")
    subparsers = parser.add_subparsers(dest="command")

    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session.")
    chat_parser.add_argument(
        "--config",
        help="Optional path to a TOML config file.",
        default=None,
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "chat":
        config = load_config(explicit_config_path=args.config)
        setup_logging(config.debug)
        return run_chat(config)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
