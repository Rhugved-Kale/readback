"""Command line entry point.

    python -m readback.cli "Refund order 4417 and log the reason."
    python -m readback.cli --demo 1

Wired to FakeAdapters. The real adapters are not implemented yet, so the CLI
runs entirely in memory and needs no network and no credentials.

TODO: add --live to swap in StripeAdapter/NotionAdapter/SlackAdapter once those
      are implemented, and require an explicit confirmation before the first
      real write.
"""

from __future__ import annotations

import argparse
import sys

from .adapters.fake import FakeAdapter
from .core.runner import run

DEMOS: dict[int, str] = {
    1: "Refund order 4417 and log the reason.",
    2: "Move Pro to $79 everywhere.",
    3: "Refund everything from last week.",
}


def build_fake_adapters() -> dict[str, FakeAdapter]:
    """One in-memory adapter per provider, all faults off."""
    return {name: FakeAdapter(name=name) for name in ("stripe", "notion", "slack")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="readback",
        description="Run an ops request and read live state back before reporting.",
    )
    parser.add_argument("request", nargs="?", help="the request text to execute")
    parser.add_argument(
        "--demo",
        type=int,
        choices=sorted(DEMOS),
        help="run one of the built-in demo requests",
    )
    parser.add_argument("--run-id", help="resume an existing run by id")
    parser.add_argument("--root", default="runs", help="where to write WALs and receipts")
    args = parser.parse_args(argv)

    if args.demo is not None:
        request_text = DEMOS[args.demo]
    elif args.request:
        request_text = args.request
    else:
        parser.error("pass a request string or --demo 1|2|3")
        return 2

    receipt = run(
        request_text,
        adapters=build_fake_adapters(),
        run_id=args.run_id,
        root=args.root,
    )
    sys.stdout.write(receipt.to_text())

    # Exit non-zero on anything that is not a clean success, so the eval harness
    # and CI can branch on it.
    return 0 if receipt.outcome == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
