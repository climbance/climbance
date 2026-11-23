"""`diagnose attempts`, `diagnose mutants`, `diagnose score` and `diagnose
verdicts`: the diagnosis call over the failed attempts or the labelled mutants,
its score per label mode, and its unscored verdicts for the spot check."""

import argparse
from dataclasses import replace

from climb.calls import CallLog
from climb.cards import CardStore
from climb.cases import CaseLog
from climb.cli.display import exit_on
from climb.cli.score import configurations
from climb.cli.transport import transport
from climb.diagnoser import DEFAULT, Tool
from climb.diagnosing import (
    Result,
    Row,
    Tasks,
    diagnose_attempts,
    diagnose_mutants,
    sample,
    scored,
    slip_mutants,
    unscored,
)
from climb.judgements import ItemStore
from climb.judging import labelled_mutants
from climb.judging.labelled import LabelledMutant
from climb.keylines import KeyLineStore
from climb.log import AttemptLog
from climb.mutant_diagnoses import MutantDiagnosisLog
from climb.problems import ProblemStore
from climb.schema import SolutionRole, TestCase
from climb.scorer import percent
from climb.solutions import SolutionLog
from climb.storage import Database


def diagnose(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    named = configurations(args, parser, DEFAULT)
    if args.subject == "verdicts" and len(named) > 1:
        parser.exit(2, "diagnose verdicts: one configuration at a time\n")
    asked: list[str] = args.tool or []
    tools = frozenset(Tool(one) for one in asked)
    sets = score_sets(tools) if args.subject == "score" else [tools]
    # no credentials asked of a run that makes no call
    stored = args.subject == "verdicts" or (args.subject == "score" and args.stored)
    log, mutant_log, calls = AttemptLog(root), MutantDiagnosisLog(root), CallLog(root)
    user = getattr(args, "user", None)
    base = Tasks(
        problems={one.id: one for one in ProblemStore(root).all()},
        templates={one.id: one for card in CardStore(root).all() for one in card.templates},
        cases={one.id: one for one in CaseLog(root).cases()},
        # later runs land later, so the latest stands
        runs={one.attempt_id: one for one in log.verifications(user)},
    )
    per = None if args.all else args.per_operator
    found = labelled_mutants(ItemStore(root).served(), KeyLineStore(root).served())
    mutants = sample(found, per)
    if args.subject in ("mutants", "score"):
        mutants += sample(slips(root, base), per)
    columns = [(one, replace(base, tools=chosen)) for one in named for chosen in sets]
    for configuration, tasks in () if stored else columns:
        api = transport(args, parser)
        on = f"{configuration.model}{label(tasks.tools)}"
        if args.subject in ("attempts", "score"):
            result = diagnose_attempts(
                api,
                log,
                calls,
                tasks,
                user_id=user,
                limit=args.limit,
                concurrency=args.concurrency,
                fresh=args.fresh,
                configuration=configuration,
            )
            report(on, "attempts", result)
            exit_on(parser, "diagnose", result)
        if args.subject in ("mutants", "score"):
            result = diagnose_mutants(
                api,
                mutant_log,
                calls,
                mutants,
                tasks,
                limit=args.limit,
                concurrency=args.concurrency,
                fresh=args.fresh,
                configuration=configuration,
            )
            report(on, "mutants", result)
            exit_on(parser, "diagnose", result)
    if args.subject == "verdicts":
        configuration, tasks = columns[0]
        for one in unscored(
            configuration,
            tasks,
            log.attempts(user),
            log.self_labels(user),
            log.diagnoses(user),
        ):
            print(one.model_dump_json())
    if args.subject == "score":
        attempts = log.attempts(user)
        labels, diagnoses, read = log.self_labels(user), log.diagnoses(user), mutant_log.all()
        scores = [
            scored(one, tasks, attempts, labels, diagnoses, mutants, read) for one, tasks in columns
        ]
        table(
            [f"{one.model.split('/')[-1]}{label(tasks.tools)}" for one, tasks in columns],
            scores,
            # each configuration's first column is its baseline
            [scores[index - index % len(sets)] for index in range(len(scores))],
        )


def score_sets(tools: frozenset[Tool]) -> list[frozenset[Tool]]:
    """The baseline, each tool alone, then every tool together."""
    alone = [frozenset({one}) for one in sorted(tools)]
    return [frozenset(), *alone, *([tools] if len(alone) > 1 else [])]


def slips(root: Database, base: Tasks) -> list[LabelledMutant]:
    """Derived on each read: every one runs a canonical's mutants."""
    canonicals: dict[str, str] = {}
    for one in SolutionLog(root).solutions():
        if one.role is SolutionRole.CANONICAL:
            canonicals.setdefault(one.problem_id, one.code)  # the first stored
    cases: dict[str, list[TestCase]] = {}
    for one in base.cases.values():
        cases.setdefault(one.problem_id, []).append(one)
    return slip_mutants(list(base.problems.values()), base.templates, canonicals, cases)


def label(tools: frozenset[Tool]) -> str:
    return "".join(f" +{one}" for one in sorted(tools))


def report(on: str, subject: str, result: Result) -> None:
    print(f"{on}, {subject}: {result.diagnosed} diagnosed, {result.skipped} read already")
    if result.unanswered:
        print(f"{result.unanswered} answered nothing; the call log holds each")
    for one in result.failed:
        print(f"failed: {one}")


def table(headers: list[str], scores: list[list[Row]], baselines: list[list[Row]]) -> None:
    """A row per label mode, a column per configuration and tool set."""
    print()
    width = max(32, *(len(one) + 2 for one in headers))
    print(f"{'':<14}{'implies':<9}" + "".join(f"{one:>{width}}" for one in headers))
    for index, row in enumerate(scores[0]):
        cells = "".join(
            f"{cell(rows[index], base[index]):>{width}}"
            for rows, base in zip(scores, baselines, strict=True)
        )
        print(f"{row.label:<14}{row.implied:<9}{cells}")


def cell(row: Row, baseline: Row | None = None) -> str:
    if row.read == 0:
        return "unread"
    # under the minimum only the count shows: `1/1` is a share by another name
    if row.share is None:
        return f"n={row.read}"
    shown = f"{percent(row.matched, row.read)} of {row.read}"
    if baseline is None or baseline is row or baseline.share is None:
        return shown
    return f"{shown}, {round((row.share - baseline.share) * 100):+d}"
