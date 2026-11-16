"""An answer decided, and the next item picked: `log.md`, Judging a solution."""

from collections.abc import Collection, Sequence
from enum import StrEnum
from typing import Protocol

from climb.schema import Fill, ItemStatus, Judgement, JudgementItem, KeyLineItem


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


def next_item[T: Served](
    items: Sequence[T],
    answers: Sequence[Answered],
    *,
    templates: Collection[str] | None = None,
) -> T | None:
    """Unseen first, then the item answered longest ago; `templates` narrows
    the pick to one card's forms."""
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
    return min(open_, key=lambda one: (one.id in last, last.get(one.id, -1), one.id))
