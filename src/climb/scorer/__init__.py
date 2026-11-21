"""A model's verdicts scored against labels, per category: `cli/eval-set.md`."""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel


class CategoryScore(BaseModel):
    """One category's row. `over` and `missed` are asymmetric failures: a
    category named too readily against one not recognised."""

    category: str
    items: int = 0  # scored items the label names it on
    exact: int = 0  # of `items`, those the machine's whole set agreed on
    missed: int = 0  # of `items`, those the machine did not name it on
    over: int = 0  # items it was named on that the label did not —

    # counted outside `items`, so the two are not a rate over one denominator


class Disagreement(BaseModel):
    """One item the label and the machine read differently. The label is ground
    truth by construction, not by being right, so which is wrong is a reader's
    question."""

    item_id: str
    truth: list[str]
    machine: list[str]


class Agreement(BaseModel):
    scored: int = 0
    exact: int = 0
    # One include/exclude decision per candidate on each scored item. Set
    # equality compounds them, so a run of near misses reads as a far worse
    # judge than it is.
    decisions: int = 0
    decisions_agreed: int = 0
    per_category: list[CategoryScore] = []
    disagreements: list[Disagreement] = []


def agreement(
    truth: Mapping[str, Sequence[str]],
    machine: Mapping[str, Sequence[str]],
    candidates: Mapping[str, Sequence[str]] | None = None,
) -> Agreement:
    """Agreement by set equality, item by item. A verdict naming no category is
    scored like any other; an item with no verdict at all is unscored, since
    nothing was read."""
    rows: dict[str, CategoryScore] = {}

    def row(category: str) -> CategoryScore:
        return rows.setdefault(category, CategoryScore(category=category))

    result = Agreement()
    for item_id, expected in truth.items():
        if item_id not in machine:
            continue
        wanted, given = set(expected), set(machine[item_id])
        agreed = wanted == given
        result.scored += 1
        result.exact += agreed
        if not agreed:
            result.disagreements.append(
                Disagreement(item_id=item_id, truth=sorted(wanted), machine=sorted(given))
            )
        for category in wanted:
            row(category).items += 1
            row(category).exact += agreed
            row(category).missed += category not in given
        # Counted outside `items`, or the category a judge reaches for wrongly
        # would be the one the score cannot see.
        for category in given - wanted:
            row(category).over += 1

    result.per_category = [rows[category] for category in sorted(rows)]
    if candidates is not None:
        result.decisions, result.decisions_agreed = per_decision(truth, machine, candidates)
    return result


def per_decision(
    truth: Mapping[str, Sequence[str]],
    machine: Mapping[str, Sequence[str]],
    candidates: Mapping[str, Sequence[str]],
) -> tuple[int, int]:
    """How many include/exclude decisions a judge got right, and of how many.

    The denominator is the candidates: declining a category correctly is the
    decision set equality never credits. A disagreement counts only where it
    names a candidate, since a stored verdict can carry a retired one.
    """
    total = agreed = 0
    for item_id, expected in truth.items():
        offered = set(candidates.get(item_id, ()))
        if item_id not in machine or not offered:
            continue
        total += len(offered)
        agreed += len(offered) - len((set(expected) ^ set(machine[item_id])) & offered)
    return total, agreed
