"""The panel's trials, the judge's correction, and the judge's ratings.

`cli/difficulty/judge.md` and `trials.md` give the design. The anchors and
their draws are read from files outside every repository, and never stored.
"""

import argparse
import csv
import hashlib
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from climb.calls import CallLog, Transport
from climb.cli.transport import transport
from climb.difficulty import (
    PANEL,
    Anchor,
    Member,
    correct,
    draw,
    rating,
    standing_correction,
    trial,
)
from climb.difficulty.judge import current
from climb.generation import Corpus
from climb.ratings import CorrectionLog, DrawLog, RatingLog
from climb.schema import DifficultyDraw, Problem, Trial, band
from climb.storage import Database
from climb.trials import TrialLog

HASH_LENGTH = 12


def difficulty(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    if args.action == "trials":
        return trials(args, parser, root)
    if args.action == "correct":
        return corrected(args, parser, root)
    return judged(args, parser, root)


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


def member_of(one: Trial) -> tuple[str, str, str]:
    return (one.model or "", one.effort or "", one.pin or "")


def key(member: Member) -> tuple[str, str, str]:
    c = member.configuration
    return (c.model, c.effort, c.pin)


def label(member: tuple[str, str, str]) -> str:
    return f"{member[0].split('/')[-1]}/{member[1]}"


def corrected(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    """The anchors' draws fitted to a correction, stored under `--write`."""
    anchors = read_anchors(args.anchors, parser)
    try:
        draws = [
            DifficultyDraw.model_validate_json(line)
            for line in args.anchor_draws.read_text().splitlines()
            if line.strip()
        ]
    except (OSError, ValueError) as exc:
        parser.exit(2, f"difficulty: {args.anchor_draws} holds no draws: {exc}\n")
    anchor_set = hashlib.sha256(args.anchors.read_bytes()).hexdigest()[:HASH_LENGTH]
    try:
        correction = correct(draws, anchors, anchor_set=anchor_set)
    except ValueError as exc:
        parser.exit(2, f"difficulty: {exc}\n")
    print(
        f"anchor set {anchor_set}: {correction.anchors_fitted} fitted,"
        f" {correction.anchors_held_out} held out, of {len(anchors)};"
        f" {correction.draws} draws a statement"
    )
    print(f"line: score = {correction.intercept:.1f} + {correction.slope:.3f} x judged")
    print(
        f"held out: Spearman {correction.held_out_spearman:.3f},"
        f" mean error {correction.held_out_mean_error:.0f}, deviation {correction.deviation:.0f}"
    )
    if not args.write:
        print("difficulty: nothing stored; --write stores the correction")
        return
    CorrectionLog(root).append(correction)
    print(f"difficulty: correction {correction.id} stored")


def judged(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    """Every served problem with no rating under the standing correction, drawn
    and rated; the draws and ratings stored only under `--write`."""
    correction = standing_correction(CorrectionLog(root).all())
    if correction is None:
        parser.exit(
            2, "difficulty: no correction matches the judge; run `difficulty correct --write`\n"
        )
    corpus = Corpus.at(root)
    ratings, draw_log = RatingLog(root), DrawLog(root)
    rated = {one.problem_id for one in ratings.all() if one.correction_id == correction.id}
    todo = [one for one in corpus.problems.all() if one.served and one.id not in rated]
    todo = todo[: args.limit]
    stored: dict[str, list[DifficultyDraw]] = {}
    for held_draw in draw_log.all():
        stored.setdefault(held_draw.problem_id, []).append(held_draw)
    print(f"difficulty: {len(todo)} problem(s) to rate under correction {correction.id[:8]}")
    sender, calls = transport(args, parser), CallLog(root)
    spend, lock, counts = Spend(args.budget), threading.Lock(), Counter[str]()

    def one(problem: Problem) -> None:
        held = [d for d in stored.get(problem.id, []) if current(d, problem.statement)]
        new = fresh(problem, correction.draws - len(held), sender, calls, spend)
        if args.write:
            for made in new:
                draw_log.append(made)
        read = (held + new)[: correction.draws]
        if len(read) < correction.draws:
            with lock:
                counts["unrated"] += 1
            return
        rated_one = rating(problem.id, read, correction)
        if args.write:
            ratings.append(rated_one)
        with lock:
            counts["rated"] += 1
            print(
                f"{problem.id[:8]} {problem.difficulty!s:<6} -> {band(rated_one.score)!s:<6}"
                f" {rated_one.score:.0f} from {[d.judged for d in read]} ${spend.spent:.4f}",
                flush=True,
            )

    with ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(one, todo))
    print(
        f"difficulty: {counts['rated']} rated, {counts['unrated']} left unrated with fewer than"
        f" {correction.draws} readable draws; spent ${spend.spent:.4f}"
    )
    if not args.write:
        print("difficulty: nothing stored; --write stores the draws and the ratings")


class Spend:
    """Dollars spent across the run's threads, against its budget."""

    def __init__(self, budget: float) -> None:
        self.budget, self.spent, self.lock = budget, 0.0, threading.Lock()

    def open(self) -> bool:
        with self.lock:
            return self.spent < self.budget

    def add(self, cost: float | None) -> None:
        with self.lock:
            self.spent += cost or 0


def fresh(
    problem: Problem, wanted: int, sender: Transport, calls: CallLog, spend: Spend
) -> list[DifficultyDraw]:
    """Up to `wanted` new draws; an unreadable reply is a draw short."""
    got: list[DifficultyDraw] = []
    for _ in range(wanted):
        if not spend.open():
            break
        try:
            call, made = draw(problem.id, problem.statement, transport=sender, calls=calls)
        except Exception as exc:  # the call is logged; the problem is drawn on the next run
            sys.stderr.write(f"{problem.id[:8]}: {exc}\n")
            break
        spend.add(call.cost)
        if made is not None:
            got.append(made)
    return got


def read_anchors(path: Path, parser: argparse.ArgumentParser) -> dict[str, Anchor]:
    """`id`, `rating` and `split` (`fit` or `held_out`), one anchor a row."""
    try:
        with path.open() as listed:
            rows = list(csv.DictReader(listed))
        return {
            row["id"]: Anchor(rating=float(row["rating"]), held_out=row["split"] == "held_out")
            for row in rows
        }
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(2, f"difficulty: {path} is no anchor list: {exc}\n")
