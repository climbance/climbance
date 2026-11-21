"""`spot draw` and `spot read`: a judge's verdicts sampled for marking, and the
marks read back into its precision per verdict kind."""

import argparse
import sys
from pathlib import Path

from climb.scorer import percent
from climb.scorer.spot import read, sheet, verdicts


def spot(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.action == "draw":
        found = verdicts(Path(args.verdicts).read_text().splitlines())
        if not found:
            parser.exit(2, f"spot draw: no verdict in {args.verdicts}\n")
        print(sheet(found, args.per_kind, args.seed))
        return
    try:
        rows = read(Path(args.sheet).read_text())
    except ValueError as error:
        parser.exit(2, f"spot read: {error}\n")
    if not rows:
        parser.exit(2, f"spot read: no kind heading in {args.sheet}\n")
    print(f"{'kind':<20}{'precision':>16}{'right':>8}{'wrong':>8}{'unmarked':>10}{'of':>8}")
    for row in rows:
        marked = row.right + row.wrong
        share = percent(row.right, marked) if marked else "unmarked"
        print(
            f"{row.kind:<20}{share:>16}{row.right:>8}{row.wrong:>8}"
            f"{row.unmarked:>10}{row.population:>8}"
        )
    if any(row.unmarked for row in rows):
        print(f"{sum(row.unmarked for row in rows)} line(s) unmarked", file=sys.stderr)
