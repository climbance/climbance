"""`climb copy-corpus`: the problems the local store landed, copied into the
deployed store with every product record naming them."""

import argparse
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import ColumnElement, Connection, Table, insert, select

from climb.calls.table import calls
from climb.cards.table import card_templates, cards
from climb.cases.table import test_cases
from climb.matches.table import template_matches
from climb.outcomes.table import site_outcomes
from climb.problems.table import problems
from climb.ratings.table import (
    difficulty_corrections,
    difficulty_draws,
    difficulty_rating_draws,
    difficulty_ratings,
)
from climb.solution_claims.table import solution_claims
from climb.solutions.table import solutions
from climb.storage import Database
from climb.trials.table import trials
from climb.verifications.table import verification_case_results, verifications

# the order a foreign key needs: every row after the rows it names
ORDER: tuple[Table, ...] = (
    calls,
    problems,
    test_cases,
    solutions,
    verifications,
    verification_case_results,
    solution_claims,
    template_matches,
    site_outcomes,
    difficulty_corrections,
    difficulty_draws,
    difficulty_ratings,
    difficulty_rating_draws,
    trials,
)

# each store's seed mints its own template ids, so a template is the same one
# in both stores by its card's slug and its own
TEMPLATE_COLUMNS: dict[Table, str] = {
    problems: "target_template_id",
    template_matches: "template_id",
    site_outcomes: "target_template_id",
}

Row = dict[str, Any]


@dataclass
class Copy:
    rows: dict[str, list[Row]] = field(default_factory=dict[str, list[Row]])
    # problems in both stores whose status moved in one of them
    moved: list[tuple[str, str, str]] = field(default_factory=list[tuple[str, str, str]])
    # templates the deployed store has not seeded, as card/template
    unseeded: list[str] = field(default_factory=list[str])
    # calls a user's request made, which never leave the store they are in
    private: list[str] = field(default_factory=list[str])

    @property
    def refused(self) -> bool:
        return bool(self.unseeded or self.private)


def read(conn: Connection, table: Table, *conditions: ColumnElement[bool]) -> list[Row]:
    order = table.c.appended if "appended" in table.c else list(table.primary_key.columns)
    query = select(table).where(*conditions)
    query = query.order_by(*order) if isinstance(order, list) else query.order_by(order)
    # `appended` is minted by the store a row lands in
    return [
        {name: value for name, value in row.items() if name != "appended"}
        for row in conn.execute(query).mappings()
    ]


def keyed(table: Table, row: Row) -> tuple[Any, ...]:
    return tuple(row[column.name] for column in table.primary_key.columns)


def templates_by_slug(conn: Connection) -> dict[str, tuple[str, str]]:
    query = select(card_templates.c.id, cards.c.slug, card_templates.c.slug).join(cards)
    return {id: (card, slug) for id, card, slug in conn.execute(query)}


def planned(source: Connection, target: Connection) -> Copy:
    """What a copy writes: each problem the target lacks, its records, and the
    calls they name. Nothing is read from a problem the target already holds."""
    plan = Copy()
    held = dict(tuple(row) for row in target.execute(select(problems.c.id, problems.c.status)))
    local = read(source, problems)
    plan.moved = [
        (row["id"], str(row["status"]), str(held[row["id"]]))
        for row in local
        if row["id"] in held and row["status"] != held[row["id"]]
    ]
    new = [row for row in local if row["id"] not in held]
    ids = {row["id"] for row in new}
    rows: dict[Table, list[Row]] = {problems: new}
    rows[test_cases] = read(source, test_cases, test_cases.c.problem_id.in_(ids))
    rows[solutions] = read(source, solutions, solutions.c.problem_id.in_(ids))
    solved = {row["id"] for row in rows[solutions]}
    rows[verifications] = read(source, verifications, verifications.c.solution_id.in_(solved))
    rows[verification_case_results] = read(
        source,
        verification_case_results,
        verification_case_results.c.verification_id.in_({row["id"] for row in rows[verifications]}),
    )
    rows[solution_claims] = read(source, solution_claims, solution_claims.c.solution_id.in_(solved))
    rows[template_matches] = read(
        source, template_matches, template_matches.c.solution_id.in_(solved)
    )
    # a writing's earlier sites name no problem, so the writing is the key
    landed = select(site_outcomes.c.writing_id).where(site_outcomes.c.problem_id.in_(ids))
    rows[site_outcomes] = read(source, site_outcomes, site_outcomes.c.writing_id.in_(landed))
    rows[difficulty_draws] = read(source, difficulty_draws, difficulty_draws.c.problem_id.in_(ids))
    rows[difficulty_ratings] = read(
        source, difficulty_ratings, difficulty_ratings.c.problem_id.in_(ids)
    )
    rows[difficulty_rating_draws] = read(
        source,
        difficulty_rating_draws,
        difficulty_rating_draws.c.rating_id.in_({row["id"] for row in rows[difficulty_ratings]}),
    )
    corrected = {row["correction_id"] for row in rows[difficulty_ratings]} - {None}
    rows[difficulty_corrections] = read(
        source, difficulty_corrections, difficulty_corrections.c.id.in_(corrected)
    )
    rows[trials] = read(source, trials, trials.c.problem_id.in_(ids))
    named = {row["call_id"] for one in rows.values() for row in one if row.get("call_id")}
    rows[calls] = read(source, calls, calls.c.id.in_(named))
    plan.private = [row["id"] for row in rows[calls] if row["user_id"] is not None]
    remapped(source, target, rows, plan)
    plan.rows = {table.name: absent(target, table, rows.get(table, [])) for table in ORDER}
    return plan


def remapped(
    source: Connection, target: Connection, rows: dict[Table, list[Row]], plan: Copy
) -> None:
    """Each template id rewritten to the one the target's seed minted."""
    theirs = {where: id for id, where in templates_by_slug(target).items()}
    ours = templates_by_slug(source)
    unseeded: set[str] = set()
    for table, column in TEMPLATE_COLUMNS.items():
        for row in rows.get(table, []):
            if row[column] is None:
                continue
            where = ours[row[column]]
            if where in theirs:
                row[column] = theirs[where]
            else:
                unseeded.add("/".join(where))
    plan.unseeded = sorted(unseeded)


def absent(target: Connection, table: Table, rows: Iterable[Row]) -> list[Row]:
    """The rows the target does not hold, by primary key, so a second copy
    writes nothing."""
    rows = list(rows)
    if not rows:
        return []
    held = {tuple(row) for row in target.execute(select(*table.primary_key.columns))}
    return [row for row in rows if keyed(table, row) not in held]


def copied(source: Database, target: Database, *, write: bool) -> Copy:
    """One transaction on the target: everything planned lands, or nothing."""
    with source.connect() as reading, target.begin() as writing:
        plan = planned(reading, writing)
        if write and not plan.refused:
            for table in ORDER:
                if plan.rows[table.name]:
                    writing.execute(insert(table), plan.rows[table.name])
    return plan


def copy_corpus(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    if not args.to:
        parser.exit(2, "copy-corpus: --to names the store to copy into\n")
    target = Database(url=args.to)
    if target.engine.url == root.engine.url:
        parser.exit(2, "copy-corpus: --to names the store DATABASE_URL already names\n")
    try:
        plan = copied(root, target, write=not args.dry_run)
    finally:
        target.close()
    for id, ours, theirs in plan.moved:
        print(f"moved  {id}  {ours} here, {theirs} there; left as it is there")
    if plan.unseeded:
        print("unseeded there: " + ", ".join(plan.unseeded))
        parser.exit(1, "copy-corpus: seed these cards in the target first; nothing copied\n")
    if plan.private:
        parser.exit(1, f"copy-corpus: {len(plan.private)} call(s) name a user; nothing copied\n")
    width = max(len(name) for name in plan.rows)
    for name, rows in plan.rows.items():
        print(f"{name:<{width}}  {len(rows)}")
    verb = "would copy" if args.dry_run else "copied"
    print(f"{verb} {len(plan.rows[problems.name])} problem(s)")
