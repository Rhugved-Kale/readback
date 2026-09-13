"""Command line entry point.

    python -m readback.cli "Refund order 4417 and log the reason."
    python -m readback.cli --demo 1

Defaults to FakeAdapters: no network, no credentials, safe to run anywhere.

    python -m readback.cli --demo 1 --live

swaps in the real Stripe/Notion/Slack adapters. Because --live spends real
money and posts to a real channel, it requires an interactive confirmation
unless --yes is passed.
"""

from __future__ import annotations

import argparse
import sys

import uuid

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


def _confirm(request_text: str) -> bool:
    """Gate the first real write behind an explicit yes."""
    sys.stderr.write(
        "\n*** --live will execute REAL writes against Stripe, Notion and Slack.\n"
        f"*** Request: {request_text}\n"
        "*** Type 'yes' to proceed: "
    )
    try:
        return input().strip().lower() == "yes"
    except (EOFError, KeyboardInterrupt):
        return False


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
    parser.add_argument(
        "--live",
        action="store_true",
        help="use the REAL Stripe/Notion/Slack adapters (spends money, posts publicly)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the --live confirmation prompt (for non-interactive use)",
    )
    parser.add_argument("--root", default="runs", help="where to write WALs and receipts")
    args = parser.parse_args(argv)

    if args.demo is not None:
        request_text = DEMOS[args.demo]
    elif args.request:
        request_text = args.request
    else:
        parser.error("pass a request string or --demo 1|2|3")
        return 2

    # The run id is generated HERE rather than inside run() because the live
    # adapters need it at construction time: Notion stamps it into the audit
    # row's Run ID column and Slack into its message marker, and both are what
    # verify() and the duplicate-suppression checks key on.
    run_id = args.run_id or f"run_{uuid.uuid4().hex[:12]}"

    if args.live:
        from .adapters.live import build_live_adapters, missing_env

        gaps = missing_env()
        if gaps:
            parser.error(f"--live needs these env vars set: {', '.join(gaps)}")
        if not args.yes and not _confirm(request_text):
            sys.stderr.write("aborted; nothing was applied\n")
            return 2
        adapters = build_live_adapters(run_id)
    else:
        adapters = build_fake_adapters()

    receipt = run(
        request_text,
        adapters=adapters,
        run_id=run_id,
        root=args.root,
    )
    sys.stdout.write(receipt.to_text())

    # Exit non-zero on anything that is not a clean success, so the eval harness
    # and CI can branch on it.
    return 0 if receipt.outcome == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
