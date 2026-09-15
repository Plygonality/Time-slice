"""CLI: briefs, dump, playbook, preview, apply-script."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from time_slice.brief import render_plain, render_set, render_slice
from time_slice.epochs import EPOCHS, EpochId, slice_seed
from time_slice.identity import AXES
from time_slice.playbook import build_playbook, to_apply_script, write_playbook
from time_slice.preview import write_preview


def _list_tags() -> str:
    counts: dict[str, int] = {}
    for pool in AXES.values():
        for frag in pool:
            for tag in frag.tags:
                counts[tag] = counts.get(tag, 0) + 1
    width = max(len(tag) for tag in counts)
    body = "\n".join(
        f"  {tag.ljust(width)}  x{counts[tag]}" for tag in sorted(counts)
    )
    return "Identity tags (epoch overlays add constructing/active/relic):\n" + body


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="identity seed (printed on every brief; reuse it)",
    )
    shared.add_argument(
        "-e",
        "--epoch",
        choices=list(EPOCHS),
        default=None,
        help="print a single epoch instead of all three",
    )
    shared.add_argument(
        "--plain",
        action="store_true",
        help="emit one-line prompts only",
    )

    parser = argparse.ArgumentParser(
        prog="time-slice",
        parents=[shared],
        description=(
            "Same seed, three epochs: under construction / operational / relic. "
            "Brief tags + decay-pass + signal-field. One playbook, three screenshot folders."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python -m time_slice --seed 1234\n"
            "  python -m time_slice playbook --seed 1234 -o playbooks/seed_1234.json\n"
            "  python -m time_slice preview --seed 1234 --out screenshots\n"
            "  python -m time_slice apply-script --seed 1234\n"
        ),
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="print identity tags and exit",
    )
    parser.add_argument(
        "--list-epochs",
        action="store_true",
        help="print the three epoch ids and exit",
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("dump", parents=[shared], help="JSON of identity + three epoch slices")

    p_play = sub.add_parser(
        "playbook", parents=[shared], help="write Habitat-kit / MCP playbook JSON"
    )
    p_play.add_argument("-o", "--output", default="-")

    p_prev = sub.add_parser(
        "preview", parents=[shared], help="write three screenshot folders + gallery"
    )
    p_prev.add_argument("--out", default="screenshots")

    p_apply = sub.add_parser(
        "apply-script",
        parents=[shared],
        help="emit a bpy script Plygon-mcp can run",
    )
    p_apply.add_argument("-o", "--output")
    p_apply.add_argument("--out-root", default="screenshots")

    sub.add_parser("list-tags", help="identity tags the pools can produce")
    sub.add_parser("list-epochs", help="the three epoch ids")
    return parser


def _resolve_seed(args: argparse.Namespace) -> int:
    if args.seed is not None:
        return args.seed
    return random.randrange(2**31)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "list_tags", False) or args.cmd == "list-tags":
        sys.stdout.write(_list_tags() + "\n")
        return 0
    if getattr(args, "list_epochs", False) or args.cmd == "list-epochs":
        sys.stdout.write("\n".join(EPOCHS) + "\n")
        return 0

    seed = _resolve_seed(args)
    slices = slice_seed(seed)

    if args.cmd == "dump":
        sys.stdout.write(json.dumps(slices.to_dict(), indent=2) + "\n")
        return 0

    if args.cmd == "playbook":
        playbook = build_playbook(seed)
        if args.output == "-":
            sys.stdout.write(playbook.dumps())
        else:
            path = write_playbook(seed, args.output)
            sys.stdout.write(f"wrote {path}\n")
        return 0

    if args.cmd == "preview":
        written = write_preview(seed, args.out)
        for role, path in written.items():
            sys.stdout.write(f"{role:12} {path}\n")
        return 0

    if args.cmd == "apply-script":
        script = to_apply_script(build_playbook(seed), output_root=args.out_root)
        if args.output:
            Path(args.output).write_text(script, encoding="utf-8")
            sys.stdout.write(f"wrote {args.output}\n")
        else:
            sys.stdout.write(script)
        return 0

    if args.epoch:
        epoch: EpochId = args.epoch
        item = slices.by_epoch(epoch)
        if args.plain:
            sys.stdout.write(item.brief + "\n")
        else:
            sys.stdout.write(
                "--- Time-slice ---\n"
                + render_slice(item, index=list(EPOCHS).index(epoch) + 1, total=3)
                + "\n"
            )
        return 0

    if args.plain:
        sys.stdout.write(render_plain(slices) + "\n")
    else:
        sys.stdout.write("--- Time-slice ---\n" + render_set(slices) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
