"""`diagnose attempts`, `diagnose mutants` and `diagnose score`: the diagnosis
call over the failed attempts or the labelled mutants, and its score per label
mode."""

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
)
from climb.judgements import ItemStore
from climb.judging import labelled_mutants
from climb.keylines import KeyLineStore
from climb.log import AttemptLog
from climb.mutant_diagnoses import MutantDiagnosisLog
from climb.problems import ProblemStore
from climb.scorer import percent
from climb.storage import Database


def diagnose(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    named = configurations(args, parser, DEFAULT)
    asked: list[str] = args.tool or []
    tools = frozenset(Tool(one) for one in asked)
    # `score` reads the baseline beside each tool; a run reads them together
    sets: list[frozenset[Tool]] = (
        [frozenset(), *(frozenset({one}) for one in sorted(tools))]
        if args.subject == "score"
        else [tools]
    )
    # no credentials asked of a run that makes no call
    stored = args.subject == "score" and args.stored
    log, mutant_log, calls = AttemptLog(root), MutantDiagnosisLog(root), CallLog(root)
    user = getattr(args, "user", None)
    base = Tasks(
        problems={one.id: one for one in ProblemStore(root).all()},
        templates={one.id: one for card in CardStore(root).all() for one in card.templates},
        cases={one.id: one for one in CaseLog(root).cases()},
        # later runs land later, so the latest stands
        runs={one.attempt_id: one for one in log.verifications(user)},
    )
    found = labelled_mutants(ItemStore(root).served(), KeyLineStore(root).served())
    mutants = sample(found, None if args.all else args.per_operator)
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
    if args.subject == "score":
        attempts = log.attempts(user)
        labels, diagnoses, read = log.self_labels(user), log.diagnoses(user), mutant_log.all()
        table(
            [f"{one.model.split('/')[-1]}{label(tasks.tools)}" for one, tasks in columns],
            [
                scored(one, tasks, attempts, labels, diagnoses, mutants, read)
                for one, tasks in columns
            ],
        )


def label(tools: frozenset[Tool]) -> str:
    return "".join(f" +{one}" for one in sorted(tools))


def report(on: str, subject: str, result: Result) -> None:
    print(f"{on}, {subject}: {result.diagnosed} diagnosed, {result.skipped} read already")
    if result.unanswered:
        print(f"{result.unanswered} answered nothing; the call log holds each")
    for one in result.failed:
        print(f"failed: {one}")


def table(headers: list[str], scores: list[list[Row]]) -> None:
    """A row per label mode, a column per configuration and tool set."""
    print()
    print(f"{'':<14}{'implies':<9}" + "".join(f"{one[-30:]:>32}" for one in headers))
    for index, row in enumerate(scores[0]):
        cells = "".join(f"{cell(rows[index]):>32}" for rows in scores)
        print(f"{row.label:<14}{row.implied:<9}{cells}")


def cell(row: Row) -> str:
    if row.read == 0:
        return "unread"
    # under the minimum only the count shows: `1/1` is a share by another name
    return (
        f"n={row.read}" if row.share is None else f"{percent(row.matched, row.read)} of {row.read}"
    )
