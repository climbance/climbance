"""The CLI: one adapter over the engine, one module per command."""

import argparse
import os
from collections.abc import Callable
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from climb.classifier import DEFAULT
from climb.cli.bench import SITES
from climb.cli.board import board
from climb.cli.card import card
from climb.cli.chance_loss import chance_loss_printed
from climb.cli.claim import claim
from climb.cli.claim_solutions import claim_solutions
from climb.cli.classify import classify
from climb.cli.diagnose import diagnose
from climb.cli.difficulty import difficulty
from climb.cli.fill import fill
from climb.cli.flags import (
    Defaults,
    command,
    configuration_arguments,
    rows,
    run_arguments,
    user_argument,
)
from climb.cli.generate import generate
from climb.cli.hand_match import hand_match
from climb.cli.invite import invitation
from climb.cli.judge import judge
from climb.cli.library import library
from climb.cli.match import match
from climb.cli.module import module, retired
from climb.cli.movement import moved
from climb.cli.problem import problem
from climb.cli.retime import retime
from climb.cli.score import score
from climb.cli.seed import BadLine, seed
from climb.cli.spot import spot
from climb.cli.user_log import user_log
from climb.diagnoser import DEFAULT as DIAGNOSER
from climb.diagnoser import Tool
from climb.diagnosing import SAMPLE
from climb.difficulty import TRIES
from climb.schema import CallSite, ProblemDifficulty, RetirementReason
from climb.scorer.spot import SAMPLE as SPOT_SAMPLE
from climb.scorer.spot import SEED as SPOT_SEED
from climb.storage import Database

# What a shell reports for a command its user stopped: 128 plus the signal.
INTERRUPTED = 130

__all__ = ["INTERRUPTED", "BadLine", "main"]


def main() -> None:
    # Before the parser, since a default reads the environment too. An exported
    # variable wins over the file, and the file is found from the working
    # directory rather than from the installed package.
    load_dotenv(find_dotenv(usecwd=True))

    parser = argparse.ArgumentParser(prog="climb")
    sub = parser.add_subparsers(dest="command", required=True)

    seed_parser = command(sub, "seed", "seed authored content into the store")
    seed_parser.add_argument("kind", choices=["cards", "knowledge"])
    seed_parser.add_argument(
        "source",
        help="cards: a JSON file or a directory of them; knowledge: a module's directory",
    )

    board_parser = command(sub, "board", "per-technique progress, derived from the log")
    board_parser.add_argument("--json", action="store_true", help="emit rows instead of a table")
    board_parser.add_argument(
        "--stale", action="store_true", help="order by recency, least recently practised first"
    )
    user_argument(board_parser)

    claim_parser = command(sub, "claim", "name the techniques a piece of code used")
    subject = claim_parser.add_subparsers(dest="subject", required=True)
    attempts_parser = subject.add_parser(
        "attempts",
        help="the user's attempts: the classifier, or the user with --by-hand",
        formatter_class=Defaults,
    )
    attempts_parser.add_argument(
        "--by-hand",
        action="store_true",
        help="ask the user, one attempt at a time; run the classifier otherwise",
    )
    attempts_parser.add_argument(
        "--technique", help="only attempts whose problem carries it; every technique otherwise"
    )
    user_argument(attempts_parser)
    by_hand = attempts_parser.add_argument_group("with --by-hand")
    by_hand.add_argument("--count", type=int, default=10, help="how many to ask about")
    by_hand.add_argument("--lines", type=int, default=120, help="lines of code to show")
    by_hand.add_argument("--seed", type=int, default=0, help="sampling order")
    by_hand.add_argument(
        "--revise", action="store_true", help="ask again about attempts already claimed"
    )
    configuration_arguments(
        by_hand,
        rows("named", "--model", opens_by_default=DEFAULT.model),
        "--model",
        model="a classifier whose claim to show beside the user's; repeatable",
        provider="the endpoint the --model before it read from",
        temperature="what the --model before it sampled at; 'default' for the provider's own",
    )
    # Unset rather than 0: "not passed" has to be a state the flag cannot
    # also be given as a value.
    by_hand.add_argument(
        "--disputed",
        type=int,
        default=None,
        help="how many of them must read it differently; every claim otherwise",
    )
    classifier = attempts_parser.add_argument_group("without --by-hand")
    classifier.add_argument(
        "--limit", type=int, help="how many attempts to claim; the whole backlog otherwise"
    )
    classifier.add_argument(
        "--redo",
        action="store_true",
        help="also re-derive claims an older model or prompt version made",
    )
    run_arguments(classifier, record="claim")

    solutions_parser = subject.add_parser(
        "solutions", help="the stored canonicals, by the classifier", formatter_class=Defaults
    )
    solutions_parser.add_argument(
        "--limit", type=int, help="how many canonicals to claim; every unclaimed one otherwise"
    )
    run_arguments(solutions_parser, record="claim")

    match_parser = command(sub, "match", "which problems exercise a card's templates")
    match_parser.add_argument(
        "--by-hand",
        action="store_true",
        help="ask the user, one solution at a time; run the matcher otherwise",
    )
    match_parser.add_argument("--card", help="one card by slug; every seeded card otherwise")
    by_hand = match_parser.add_argument_group("with --by-hand")
    by_hand.add_argument("--count", type=int, default=10, help="how many to ask about")
    by_hand.add_argument("--seed", type=int, default=0, help="sampling order")
    by_hand.add_argument(
        "--verdict", action="store_true", help="show what the matcher read the same pairs as"
    )
    matcher = match_parser.add_argument_group("without --by-hand")
    matcher.add_argument(
        "--limit", type=int, help="how many pairs to read; every outstanding one otherwise"
    )
    run_arguments(matcher, record="record", question="question")

    generate_parser = command(sub, "generate", "write problems for one of a card's templates")
    generate_parser.add_argument("--card", help="the card, by slug; narrows --gaps to it")
    generate_parser.add_argument("--template", help="its template, by slug")
    generate_parser.add_argument(
        "--gaps",
        action="store_true",
        help="write for every core template carrying no match, rather than one named",
    )
    generate_parser.add_argument("--count", type=int, default=1, help="how many problems to write")
    generate_parser.add_argument(
        "--difficulty",
        type=ProblemDifficulty,
        choices=list(ProblemDifficulty),
        help="the level the generator writes for; it picks one itself otherwise",
    )
    generate_parser.add_argument(
        "--replay",
        action="store_true",
        help="re-ask the answering sites about the stored problems, writing nothing to the corpus",
    )
    generate_parser.add_argument(
        "--only",
        metavar="SITE",
        type=CallSite,
        action="append",
        help="with --replay, ask this site alone; repeatable, and every site otherwise",
    )
    generate_parser.add_argument(
        "--resume",
        action="store_true",
        help="carry every held draft forward, from the step its bench or its own state moved",
    )
    generate_parser.add_argument(
        "--drafts",
        action="store_true",
        help="list the stored drafts, naming the step each would resume at, without calling",
    )
    generate_parser.add_argument(
        "--all",
        action="store_true",
        help="with --drafts, list the rejected ones too; only what a sweep reaches otherwise",
    )
    generate_parser.add_argument(
        "--draft",
        metavar="ID",
        help="read one stored draft whole, by id or a prefix of one, without calling",
    )
    generate_parser.add_argument(
        "--reject",
        metavar="ID",
        help="reject one held draft by hand, as unexercised: no resume would separate it",
    )
    generate_parser.add_argument(
        "--limit", type=int, help="how many stored problems to replay; every one otherwise"
    )
    generate_parser.add_argument(
        "--fresh",
        action="store_true",
        help="replay a pair even where a record answers the same prompt",
    )
    sited = rows("sites", "--site")
    generate_parser.add_argument(
        "--site",
        metavar="SITE",
        choices=SITES,
        help=f"the call site the settings after it configure: {', '.join(SITES)}; repeatable",
        **sited,
    )
    configuration_arguments(generate_parser, sited, "--site")

    problem_parser = command(sub, "problem", "retire a stored problem, or rate it by hand")
    problem_parser.add_argument(
        "id", nargs="?", help="the problem --rate scores, by id or a prefix of one"
    )
    problem_parser.add_argument(
        "--retire",
        metavar="ID",
        help="read one problem whole, then retire it under --reason once confirmed",
    )
    problem_parser.add_argument(
        "--reason",
        type=RetirementReason,
        choices=list(RetirementReason),
        default=RetirementReason.DEFECTIVE,
        help="why --retire retires it: defective leaves mastery, copied stays in it",
    )
    problem_parser.add_argument(
        "--rate",
        type=float,
        metavar="SCORE",
        help="score the problem the id names by hand, on the contest scale; its band is the label",
    )

    difficulty_parser = command(
        sub, "difficulty", "the panel's trials, and the judge's correction and ratings"
    )
    difficulty_action = difficulty_parser.add_subparsers(dest="action", required=True)
    trials_parser = difficulty_action.add_parser(
        "trials",
        help="every panel member's tries on every served problem",
        formatter_class=Defaults,
    )
    trials_parser.add_argument(
        "--tries", type=int, default=TRIES, help="tries per member per problem"
    )
    trials_parser.add_argument("--workers", type=int, default=6, help="calls in flight at once")
    trials_parser.add_argument(
        "--budget", type=float, default=10.0, help="dollars, then no new call"
    )
    correct_parser = difficulty_action.add_parser(
        "correct",
        help="fit the judge's line to the contest scale on the anchors' draws",
        formatter_class=Defaults,
    )
    correct_parser.add_argument(
        "--anchors", type=Path, required=True, help="CSV: id, rating, split"
    )
    correct_parser.add_argument(
        "--anchor-draws", type=Path, required=True, help="the anchors' draws, JSON lines"
    )
    correct_parser.add_argument("--write", action="store_true", help="store the correction")
    judge_parser = difficulty_action.add_parser(
        "judge",
        help="rate every served problem the standing correction has not",
        formatter_class=Defaults,
    )
    judge_parser.add_argument("--workers", type=int, default=12, help="calls in flight at once")
    judge_parser.add_argument(
        "--limit", type=int, help="rate at most this many problems; every unrated one otherwise"
    )
    judge_parser.add_argument("--budget", type=float, default=1.0, help="dollars, then no new call")
    judge_parser.add_argument(
        "--write", action="store_true", help="store the draws and the ratings"
    )

    command(
        sub, "retime", "every served canonical at the drill cap, and its cases past a tenth of it"
    )

    score_parser = command(sub, "score", "the classifier against the user's own claims")
    score_parser.add_argument(
        "--limit",
        type=int,
        help="how many attempts to read per classifier; every unread one otherwise",
    )
    configuration_arguments(
        score_parser,
        rows("named", "--model", opens_by_default=DEFAULT.model),
        "--model",
        model="a classifier to score; repeatable",
    )
    score_parser.add_argument(
        "--stored",
        action="store_true",
        help="score only claims already stored, making no call",
    )
    score_parser.add_argument(
        "--splits",
        action="store_true",
        help="print the per-technique table and every attempt read differently; counted otherwise",
    )
    run_arguments(score_parser, record="claim", per=" per model and endpoint")
    user_argument(score_parser)

    movement_parser = command(
        sub, "movement", "how far the classifier's claims move the board off the fallback"
    )
    user_argument(movement_parser)

    invite_parser = command(sub, "invite", "the emails allowed to sign in")
    invite_action = invite_parser.add_subparsers(dest="action", required=True)
    invite_add = invite_action.add_parser("add", help="let the email sign in, or set its role")
    invite_add.add_argument("email")
    invite_add.add_argument(
        "--author", action="store_true", help="let it reach the author pages; a learner otherwise"
    )
    invite_action.add_parser("remove", help="stop the email signing in").add_argument("email")
    invite_action.add_parser("list", help="every email invited")

    command(sub, "chance-loss", "the chance to solve scored by log-loss on the cold sittings")

    diagnose_parser = command(sub, "diagnose", "where a failed solution's fault lies")
    diagnosed = diagnose_parser.add_subparsers(dest="subject", required=True)
    on_attempts = diagnosed.add_parser("attempts", help="the failed attempts with code")
    on_mutants = diagnosed.add_parser("mutants", help="the labelled mutants, sampled per operator")
    on_score = diagnosed.add_parser(
        "score", help="the call scored per label mode, after reading what it has not"
    )
    on_score.add_argument("--stored", action="store_true", help="score what is stored, no call")
    on_verdicts = diagnosed.add_parser(
        "verdicts", help="the verdicts no self-label scores, as `spot draw` reads them"
    )
    for one in (on_attempts, on_verdicts):
        one.set_defaults(per_operator=SAMPLE, all=False)
    for one in (on_attempts, on_score, on_verdicts):
        user_argument(one)
    on_verdicts.add_argument(
        "--tool", action="append", choices=[tool.value for tool in Tool], help="the tool set"
    )
    configuration_arguments(
        on_verdicts,
        rows("named", "--model", opens_by_default=DIAGNOSER.model),
        "--model",
        model="the diagnosis configuration",
    )
    for one in (on_mutants, on_score):
        one.add_argument("--per-operator", type=int, default=SAMPLE, help="mutants per operator")
        one.add_argument("--all", action="store_true", help="every labelled mutant")
    for one in (on_attempts, on_mutants, on_score):
        one.add_argument("--limit", type=int, help="ask about at most this many")
        one.add_argument(
            "--tool",
            action="append",
            choices=[tool.value for tool in Tool],
            help="evidence beyond the baseline; repeatable",
        )
        configuration_arguments(
            one,
            rows("named", "--model", opens_by_default=DIAGNOSER.model),
            "--model",
            model="a diagnosis configuration; repeatable",
        )
        run_arguments(one, record="diagnosis", per=" per model and endpoint")

    spot_parser = command(sub, "spot", "a judge's verdicts sampled for marking by hand")
    spot_action = spot_parser.add_subparsers(dest="action", required=True)
    on_draw = spot_action.add_parser(
        "draw", help="print a sheet of verdicts drawn per kind", formatter_class=Defaults
    )
    on_draw.add_argument("verdicts", help="a JSON-lines file: an id, a kind and a text per line")
    on_draw.add_argument("--per-kind", type=int, default=SPOT_SAMPLE, help="verdicts per kind")
    on_draw.add_argument("--seed", type=int, default=SPOT_SEED, help="the draw's seed")
    on_read = spot_action.add_parser("read", help="the judge's precision per kind, from the marks")
    on_read.add_argument("sheet", help="a sheet `spot draw` printed, marked")

    judge_parser = command(sub, "judge", "the judging exercise's items")
    judge_action = judge_parser.add_subparsers(dest="action", required=True)
    judge_action.add_parser(
        "build", help="build items for every template not yet served at its current code"
    )

    fill_parser = command(sub, "fill", "the key-line exercise's items")
    fill_action = fill_parser.add_subparsers(dest="action", required=True)
    fill_action.add_parser(
        "build", help="build items for every template not yet served at its current code"
    )

    card_parser = command(sub, "card", "an authored card's file, before it is seeded")
    card_action = card_parser.add_subparsers(dest="action", required=True)
    card_check = card_action.add_parser(
        "check", help="the schema, the graph, the cases and the mutants they leave standing"
    )
    card_check.add_argument("cards", nargs="+", help="card files, or slugs under content/cards")
    card_check.add_argument(
        "--no-mutants", action="store_true", help="skip running each template's mutants"
    )
    card_check.add_argument("--json", action="store_true", help="emit the findings as JSON")

    module_parser = command(sub, "module", "a knowledge module's authored files")
    module_action = module_parser.add_subparsers(dest="action", required=True)
    check_parser = module_action.add_parser(
        "check", help="hold a module to the rules docs/authoring/rules.md tags check"
    )
    check_parser.add_argument("slug", help="the module's directory under --content")
    check_parser.add_argument(
        "--content", default="content/modules", help="the directory holding the modules"
    )
    check_parser.add_argument(
        "--no-run", action="store_true", help="skip rules 1-5, which run code"
    )
    check_parser.add_argument(
        "--no-versions",
        action="store_true",
        help="skip rule 5, which runs every snippet on the older interpreters",
    )
    check_parser.add_argument(
        "--fresh", action="store_true", help="run everything again, ignoring the kept results"
    )
    check_parser.add_argument(
        "--near",
        nargs="?",
        const="",
        metavar="ID",
        help="list the questions explained most alike, for one id or for all, and stop",
    )
    check_parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    check_parser.add_argument(
        "--sub", help="report one subtopic's findings, and the rest of the module as counts"
    )
    status_parser = module_action.add_parser(
        "status", help="print which subtopics the module has written at each level"
    )
    status_parser.add_argument("slug", help="the module's directory under --content")
    status_parser.add_argument(
        "--content", default="content/modules", help="the directory holding the modules"
    )
    status_parser.add_argument("--json", action="store_true", help="emit the status as JSON")
    retire_parser = module_action.add_parser(
        "retire", help="retire a seeded module whose files are gone, keeping its rows"
    )
    retire_parser.add_argument("slug", help="the module's slug in the store")

    library_parser = command(sub, "library", "the sources a module's concepts cite")
    library_action = library_parser.add_subparsers(dest="action", required=True)
    refresh_parser = library_action.add_parser(
        "refresh", help="fetch every cited source again, and report the quotes a change breaks"
    )
    refresh_parser.add_argument("--module", help="refresh the sources of this module alone")
    refresh_parser.add_argument(
        "--content", default="content", help="the content repository, holding modules/ and library/"
    )
    refresh_parser.add_argument("--json", action="store_true", help="emit the refresh as JSON")

    log_parser = command(
        sub, "log", "one user's whole log, read out or erased, or the account deleted"
    )
    action = log_parser.add_subparsers(dest="action", required=True)
    export_parser = action.add_parser("export", help="print every record of the log as JSON")
    user_argument(export_parser)
    erase_parser = action.add_parser("erase", help="delete every record of the log")
    # named every time: a default would erase the author's own log
    erase_parser.add_argument("--user", required=True, help="whose log to erase")
    delete_parser = action.add_parser(
        "delete", help="erase the log and delete the account, as the account menu does"
    )
    delete_parser.add_argument("--user", required=True, help="whose account to delete")
    action.add_parser("prune", help="delete every uninvited account no sign-in used for a year")

    args = parser.parse_args()
    # read at call time, not at import: a test names its own database
    root = Database(url=os.environ.get("DATABASE_URL"))
    try:
        dispatch(args, parser, root)
    except KeyboardInterrupt:
        # Not a fault: every command appends as it goes, so what landed is
        # kept and a traceback would name only where the user was.
        parser.exit(INTERRUPTED, "\ninterrupted\n")
    finally:
        root.close()


# every command takes the parser, whether or not it exits through it
COMMANDS: dict[str, Callable[[argparse.Namespace, argparse.ArgumentParser, Database], None]] = {
    "seed": seed,
    "board": lambda args, _parser, root: board(args, root),
    # one command per record; the subject names the code, `--by-hand` the writer
    "claim": lambda args, parser, root: (
        claim_solutions if args.subject == "solutions" else claim if args.by_hand else classify
    )(args, parser, root),
    "problem": problem,
    "difficulty": difficulty,
    "retime": lambda _args, _parser, root: retime(root),
    "generate": generate,
    "match": lambda args, parser, root: (hand_match if args.by_hand else match)(args, parser, root),
    "score": score,
    "movement": moved,
    "log": user_log,
    "card": lambda args, parser, _root: card(args, parser),
    "judge": lambda args, _parser, root: judge(args, root),
    "fill": lambda args, _parser, root: fill(args, root),
    "module": lambda args, parser, root: (
        retired(args, root) if args.action == "retire" else module(args, parser)
    ),
    "library": lambda args, parser, _root: library(args, parser),
    "invite": invitation,
    "chance-loss": lambda _args, _parser, root: chance_loss_printed(root),
    "diagnose": diagnose,
    "spot": lambda args, parser, _root: spot(args, parser),
}


def dispatch(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    COMMANDS[args.command](args, parser, root)
