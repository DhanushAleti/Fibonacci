"""Minimal command-line entry point for PHI.

Phase 0 exposes only introspection commands (``version``, ``info``). Research
commands are added as their phases land, so the CLI never advertises capability
that does not yet exist (documentation-integrity principle in the mission brief).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from phi import PHI, __version__
from phi.config import Settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phi",
        description="PHI research platform — falsifiable evaluation of Golden Ratio "
        "features in markets.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version", help="print the PHI version")
    sub.add_parser("info", help="print resolved settings (no secrets)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "info":
        settings = Settings.from_env()
        print(f"phi {__version__}")
        print(f"phi constant: {PHI:.16f}")
        print(f"repo root: {settings.paths.root}")
        print(f"random seed: {settings.random_seed}")
        print(f"log level: {settings.log_level}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
