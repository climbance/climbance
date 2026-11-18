"""An answer decided, and the next item picked: `api/short-exercises.md`."""

from collections.abc import Collection, Iterable, Mapping, Sequence
from enum import StrEnum
from typing import Protocol

from climb.cards.graph import depths
from climb.schema import Card, Fill, ItemStatus, Judgement, JudgementItem, KeyLineItem


class Verdict(StrEnum):
    RIGHT = "right"  # a clean item called clean
    FALSE_ALARM = "false_alarm"  # a clean item called flawed
    LOCATED = "located"  # a flaw called flawed, on its own line
    SPOTTED = "spotted"  # a flaw called flawed, on another line
    MISSED = "missed"  # a flaw called clean


def verdict(item: JudgementItem, answer: Judgement) -> Verdict:
    if item.clean:
        return Verdict.RIGHT if answer.called_clean else Verdict.FALSE_ALARM
    if answer.called_clean:
        return Verdict.MISSED
    return Verdict.LOCATED if answer.line == item.line else Verdict.SPOTTED


class Served(Protocol):
    @property
    def id(self) -> str: ...
    @property
    def template_id(self) -> str: ...
    @property
    def status(self) -> ItemStatus: ...


class Answered(Protocol):
    @property
    def item_id(self) -> str: ...


def filled(item: KeyLineItem, answer: Fill) -> bool:
    return answer.choice < len(item.choices) and item.choices[answer.choice].correct


type Place = tuple[bool, int, str]  # card not started, its depth, its slug


def places(cards: Iterable[Card], started: Collection[str]) -> dict[str, Place]:
    """Each template's card's place in the draw, by template id. `started`
    holds the ids of the cards the user started."""
    deep = depths(cards := list(cards))
    return {
        one.id: (card.id not in started, deep[card.slug], card.slug)
        for card in cards
        for one in card.templates
    }


def next_item[T: Served](
    items: Sequence[T],
    answers: Sequence[Answered],
    places: Mapping[str, Place],
    *,
    templates: Collection[str] | None = None,
) -> T | None:
    """A started card's item first, unseen before the one answered longest
    ago: `api/short-exercises.md`. `templates` narrows the draw to one
    card's forms."""
    last: dict[str, int] = {}
    for order, one in enumerate(answers):
        last[one.item_id] = order
    open_ = [
        one
        for one in items
        if one.status is ItemStatus.SERVED and (templates is None or one.template_id in templates)
    ]
    if not open_:
        return None

    def key(one: T) -> tuple[bool, bool, int, int, str, str]:
        later, depth, slug = places[one.template_id]
        return (later, one.id in last, last.get(one.id, -1), depth, slug, one.id)

    return min(open_, key=key)
