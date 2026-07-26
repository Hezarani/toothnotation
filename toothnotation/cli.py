"""Command-line interface for toothnotation.

Examples::

    toothnotation convert 36 fdi universal      # -> 19
    toothnotation convert 19 universal fdi        # -> 36
    toothnotation info 36                          # full detail, auto-detected
    toothnotation chart                            # print the permanent chart
"""

from __future__ import annotations

import argparse
import sys

from . import SYSTEMS, __version__, all_teeth, convert, detect_system, parse


def _cmd_convert(args: argparse.Namespace) -> int:
    try:
        print(convert(args.value, args.from_system, args.to_system))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    try:
        t = parse(args.value, args.system)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    detected = args.system or detect_system(args.value)
    print(f"{t.name}")
    print(f"  detected   {detected}")
    print(f"  FDI        {t.fdi}")
    print(f"  Universal  {t.universal}")
    print(f"  Palmer     {t.palmer.quadrant} {t.palmer.symbol}")
    print(f"  dentition  {t.dentition}")
    print(f"  arch/side  {t.arch} / {t.side}")
    return 0


def _cmd_chart(args: argparse.Namespace) -> int:
    teeth = all_teeth(args.dentition)
    by_quad: dict[str, list] = {}
    for t in teeth:
        by_quad.setdefault(t.quadrant, []).append(t)

    def render(quadrants, reverse_first):
        cells = []
        for qi, q in enumerate(quadrants):
            row = sorted(by_quad[q], key=lambda x: x.position)
            if (qi == 0) == reverse_first:
                row = list(reversed(row))
            cells.append(" ".join(f"{t.to(args.system):>3}" for t in row))
        return "  |  ".join(cells)

    print(f"[{args.dentition} · {args.system}]  (as if facing the patient)")
    print("upper:", render(["UR", "UL"], reverse_first=True))
    print("lower:", render(["LR", "LL"], reverse_first=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="toothnotation", description=__doc__.splitlines()[0])
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("convert", help="convert a code between systems")
    c.add_argument("value")
    c.add_argument("from_system", choices=SYSTEMS)
    c.add_argument("to_system", choices=SYSTEMS)
    c.set_defaults(func=_cmd_convert)

    i = sub.add_parser("info", help="show full detail for a tooth")
    i.add_argument("value")
    i.add_argument("system", nargs="?", choices=SYSTEMS, default=None)
    i.set_defaults(func=_cmd_info)

    ch = sub.add_parser("chart", help="print a dental chart")
    ch.add_argument("--system", choices=SYSTEMS, default="fdi")
    ch.add_argument("--dentition", choices=["permanent", "primary"], default="permanent")
    ch.set_defaults(func=_cmd_chart)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
