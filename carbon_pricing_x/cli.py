from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _app_script_path() -> Path:
    return Path(__file__).resolve().parent / "streamlit_app.py"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="carbonpricingx", description="CarbonPricingX CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Launch Streamlit app")
    run_parser.add_argument("--port", type=int, default=None, help="Port for Streamlit server")
    run_parser.add_argument("--headless", action="store_true", help="Run Streamlit headless")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command in {None, "run"}:
        cmd = [sys.executable, "-m", "streamlit", "run", str(_app_script_path())]
        if args.port is not None:
            cmd += ["--server.port", str(args.port)]
        if args.headless:
            cmd += ["--server.headless", "true"]
        return subprocess.call(cmd)

    parser.print_help()
    return 0
