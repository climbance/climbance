"""The panel's trials on the corpus, and a difficulty fit over them.

`corpus.md` `### Difficulty fits` gives the design. The anchors are read from
files outside every repository, named on the command line, and never stored.
"""

import argparse
import csv
import hashlib
import json
import statistics
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from climb.calls import CallLog
from climb.cli.transport import transport
from climb.difficulty import PANEL, Anchor, Member, calibrate, trial
from climb.difficulty.calibrate import member_of
from climb.generation import Corpus
from climb.ratings import FitLog
from climb.schema import Problem, Trial, band
from climb.storage import Database
from climb.trials import TrialLog

HASH_LENGTH = 12


def difficulty(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    if args.action == "trials":
        return trials(args, parser, root)
    return fitted(args, parser, root)


def trials(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    """Every member's tries on every served problem, skipping those stored."""
    corpus = Corpus.at(root)
    served = [one for one in corpus.problems.all() if one.served]
    log, calls = TrialLog(root), CallLog(root)
    done = {(one.problem_id, member_of(one), one.try_number) for one in log.all()}
    jobs = [
        (problem, member, n)
        for n in range(1, args.tries + 1)
        for member in PANEL
        for problem in served
        if (problem.id, key(member), n) not in done
    ]
    print(f"difficulty: {len(jobs)} trial(s) to run over {len(served)} problem(s)")
    sender = transport(args, parser)
    lock, spent, judging = threading.Lock(), [0.0], threading.Semaphore(1)

    def one(job: tuple[Problem, Member, int]) -> None:
        problem, member, n = job
        with lock:
            if spent[0] >= args.budget:
                return
        cases = corpus.cases.for_problem(problem.id)
        try:
            made = trial(problem, cases, member, n, transport=sender, calls=calls, judging=judging)
        except Exception as exc:  # the call is logged; the trial is retried on the next run
            sys.stderr.write(f"{problem.id[:8]} {label(key(member))} try {n}: {exc}\n")
            return
        log.append(made)
        with lock:
            spent[0] += made.cost or 0
            print(
                f"{problem.id[:8]} {label(key(member)):<34} {made.outcome}"
                f" {made.cases_passed}/{made.cases_run} ${spent[0]:.3f}",
                flush=True,
            )

    with ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(one, jobs))
    print(f"difficulty: spent ${spent[0]:.3f}")


def key(member: Member) -> tuple[str, str, str]:
    c = member.configuration
    return (c.model, c.effort, c.pin)


def label(member: tuple[str, str, str]) -> str:
    return f"{member[0].split('/')[-1]}/{member[1]}"


def fitted(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    """A fit read out; stored with its ratings only under `--write`."""
    anchors = read_anchors(args.anchors, parser)
    anchored = [
        Trial.model_validate_json(line)
        for line in args.anchor_trials.read_text().splitlines()
        if line.strip()
    ]
    anchored = [one for one in anchored if one.problem_id in anchors]
    corpus = Corpus.at(root)
    served = {one.id: one for one in corpus.problems.all() if one.served}
    stored = [one for one in TrialLog(root).all() if one.problem_id in served]
    if not stored:
        parser.exit(
            2, "difficulty: no trial on a served problem is stored; run `difficulty trials`\n"
        )
    anchor_set = hashlib.sha256(args.anchors.read_bytes()).hexdigest()[:HASH_LENGTH]
    order = [key(member) for member in PANEL]
    try:
        fit, ratings = calibrate(stored, anchored, anchors, anchor_set=anchor_set, order=order)
    except ValueError as exc:
        parser.exit(2, f"difficulty: {exc}\n")

    print(
        f"anchor set {anchor_set}: {fit.anchors_fitted} fitted,"
        f" {fit.anchors_held_out} held out; {fit.problems} problem(s)"
    )
    print(f"link: score = {fit.slope:.1f} x difficulty + {fit.intercept:.1f}")
    print(
        f"held-out log-loss {fit.held_out_log_loss:.3f}, against"
        f" {fit.baseline_log_loss:.3f} from each member's solve rate"
    )
    for member in fit.members:
        print(
            f"  {label((member.model, member.effort, member.pin)):<34}"
            f" ability {member.ability:+.2f} over {member.trials} trial(s)"
        )
    labels = Counter[tuple[str, str]]()
    by_label: dict[str, list[float]] = {}
    for rating in ratings:
        aimed = str(served[rating.problem_id].difficulty)
        labels[aimed, str(band(rating.score))] += 1
        by_label.setdefault(aimed, []).append(rating.score)
    for aimed, scores in sorted(by_label.items()):
        print(
            f"  {aimed:<6} {len(scores):>3}: median {statistics.median(scores):.0f},"
            f" range {min(scores):.0f} to {max(scores):.0f}"
        )
    deviations = sorted(one.deviation or 0 for one in ratings)
    print(f"deviation: median {statistics.median(deviations):.0f}, largest {deviations[-1]:.0f}")
    print(
        "generator's label -> band: "
        + ", ".join(f"{a}->{b} {n}" for (a, b), n in sorted(labels.items()))
    )
    if args.scores:
        rows = [
            {
                "problem_id": one.problem_id,
                "aimed": str(served[one.problem_id].difficulty),
                "score": round(one.score, 1),
                "deviation": round(one.deviation or 0, 1),
            }
            for one in ratings
        ]
        args.scores.write_text("".join(json.dumps(row) + "\n" for row in rows))
    if not args.write:
        print("difficulty: nothing stored; --write stores the fit and its ratings")
        return
    FitLog(root).append(fit, ratings)
    print(f"difficulty: fit {fit.id} stored with {len(ratings)} rating(s)")


def read_anchors(path: Path, parser: argparse.ArgumentParser) -> dict[str, Anchor]:
    """`id`, `rating` and `split` (`fit` or `held_out`), one anchor a row."""
    try:
        rows = list(csv.DictReader(path.open()))
        return {
            row["id"]: Anchor(rating=float(row["rating"]), held_out=row["split"] == "held_out")
            for row in rows
        }
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(2, f"difficulty: {path} is no anchor list: {exc}\n")
