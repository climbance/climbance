import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from climb.calls import UNSENT, CallLog, ask
from climb.cli.transport import transport
from climb.knowledge import retire_module
from climb.knowledge.authoring import Checked, check, in_sub, load, near
from climb.knowledge.authoring.reverify import Check, appended, owed, witnessed
from climb.knowledge.authoring.status import markdown, topics
from climb.schema import Configuration
from climb.storage import Database

# set once the run has restarted itself with the module's libraries
RESTARTED = "CHECK_REQUIREMENTS"


def retired(args: argparse.Namespace, root: Database) -> None:
    try:
        count = retire_module(args.slug, root=root)
    except LookupError as error:
        sys.exit(f"module retire: {error}")
    print(f"{args.slug}: {count} rows retired")


# the default a chat client starts from: the claim is about models as used
SYSTEM = "You are a helpful assistant."


def configured(entry: str) -> Configuration:
    # `model@pin`, sent at the model's own effort and temperature
    model, _, pin = entry.partition("@")
    if not model or not pin:
        raise ValueError(f"panel entry {entry!r} is not model@pin")
    return Configuration(model=model, effort=UNSENT, pin=pin, temperature=None)


def reverify(
    args: argparse.Namespace, parser: argparse.ArgumentParser, root: Path, store: Database
) -> None:
    course = load(root)
    every = course.models.get("every_days")
    if not course.models.get("panel") or not isinstance(every, int):
        parser.exit(2, "module reverify: check.toml names no [models] panel and every_days\n")
    try:
        panel = {entry: configured(entry) for entry in course.models["panel"]}
    except ValueError as error:
        parser.exit(2, f"module reverify: {error}\n")
    today = date.today()
    found = owed(course, today)
    if not found:
        print(f"{args.slug}: no claim is due")
        return
    send, log = transport(args, parser), CallLog(store)

    def asking(model: str, prompt: str) -> str:
        if model not in panel:
            raise ValueError(f"{model} is not on the panel")
        _call, text = ask(send, log, system=SYSTEM, content=prompt, configuration=panel[model])
        if text is None:
            raise ValueError(f"{model} answered nothing")
        return text

    failed = 0
    for name, models in found.items():
        concept = course.concepts[name]
        checks: list[Check] = []
        for model in models:
            try:
                holds, measured = witnessed(concept["model_witness"], model, asking)
            # one model's failure leaves the rest to run
            except Exception as error:
                print(f"{name} on {model}: not checked: {type(error).__name__}: {error}")
                failed += 1
                continue
            checks.append(Check(name, model, today, holds, measured))
            print(f"{name} on {model}: {'holds' if holds else 'fails'}, {measured}")
        if checks:
            appended(root / concept["_file"], checks)
    if failed:
        parser.exit(1, f"module reverify: {failed} checks not made\n")


def status(args: argparse.Namespace, root: Path) -> None:
    found = topics(root)
    if args.json:
        rows = [
            {
                "topic": t.slug,
                "subtopic": s.slug,
                "levels": {n: vars(w) for n, w in s.levels.items()},
            }
            for t in found
            for s in t.subtopics
        ]
        print(json.dumps(rows, indent=2))
    else:
        print(markdown(args.slug, found), end="")


def module(args: argparse.Namespace, parser: argparse.ArgumentParser, store: Database) -> None:
    root = Path(args.content) / args.slug
    if not (root / "course.toml").exists():
        parser.exit(2, f"module {args.action}: no module at {root}\n")
    if args.action == "status":
        status(args, root)
        return
    requirements = root / "requirements.txt"
    if requirements.exists() and os.environ.get(RESTARTED) != str(requirements):
        # snippets run on this interpreter, which holds the module's libraries
        os.environ[RESTARTED] = str(requirements)
        argv = ["uv", "run", "--with-requirements", str(requirements), "climb"]
        os.execvp("uv", [*argv, *sys.argv[1:]])
    if args.action == "reverify":
        reverify(args, parser, root, store)
        return
    if args.near is not None:
        for line in near(load(root), args.near):
            print(line)
        return
    checked = check(
        root, run=not args.no_run, other_versions=not args.no_versions, fresh=args.fresh
    )
    elsewhere = ""
    if args.sub:
        report, named = checked.report, in_sub(load(root), args.sub)
        errors = [e for e in report.errors if named(e)]
        warnings = [w for w in report.warnings if named(w)]
        others = (len(report.errors) - len(errors), len(report.warnings) - len(warnings))
        report.errors, report.warnings = errors, warnings
        elsewhere = f"outside {args.sub}: {others[0]} errors, {others[1]} warnings"
    if args.json:
        report = checked.report
        whole = {
            "errors": report.errors,
            "warnings": report.warnings,
            "ran": checked.ran,
            "missing": report.missing,
        }
        print(json.dumps(whole, indent=2))
    else:
        for line in summary(checked):
            print(line)
        if elsewhere:
            print(elsewhere)
    if checked.report.errors:
        parser.exit(1)


def summary(checked: Checked) -> list[str]:
    report = checked.report
    found = [f"warning {line}" for line in sorted(report.warnings)]
    found += [f"error   {line}" for line in sorted(report.errors)]
    runs = ", ".join(f"{n} {kind}" for kind, n in checked.ran.items())
    if checked.ran:
        runs += f", {checked.executed} of them executed and the rest kept"
    total = f"{len(report.errors)} errors, {len(report.warnings)} warnings"
    found.append(total + (f"; ran {runs}" if runs else ""))
    if report.missing:
        names = ", ".join(f"{name} ({n})" for name, n in sorted(report.missing.items()))
        found.append(f"not run, importing a module that is not installed: {names}")
    if report.fragments:
        found.append(
            f"not compared: {report.fragments} output snippets that need what their prompt "
            "describes, and raise NameError or SyntaxError alone"
        )
    if report.unreplayed:
        found.append(
            f"not replayed: {', '.join(report.unreplayed)}, which read a file the transcript "
            "does not show"
        )
    if report.made_up:
        found.append(
            f"not run: {report.made_up} snippets importing a module check.toml lists as made up"
        )
    return found
