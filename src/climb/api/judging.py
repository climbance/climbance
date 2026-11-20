"""The judging exercise's routes: an item served without its answer, and an
answer decided. `web-app/pages/cards/judging/`."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from climb.api.context import Root, UserId
from climb.cards import CardStore
from climb.ids import new_id
from climb.judgements import ItemStore
from climb.judging import Place, Verdict, next_item, places, verdict
from climb.log import CardRunLog, JudgementLog
from climb.schema import Card, CaseOutcome, Judgement, Template

router = APIRouter(prefix="/judging")


class JudgeExample(BaseModel):
    """One of the template's cases, which states what the code must do."""

    args: list[Any]
    expected: Any


class JudgedItem(BaseModel):
    """An item as the page shows it: no field says whether it is clean."""

    item_id: str
    card_slug: str
    card_title: str
    template_title: str
    # what the form answers: its trigger's first sentence
    asks: str
    example: JudgeExample
    lines: list[str]


class JudgeAnswer(BaseModel):
    called_clean: bool
    line: int | None = None


class SeparatingCase(BaseModel):
    args: list[Any]
    expected: Any
    outcome: CaseOutcome  # wrong or crashed
    returned: Any  # what the flawed code gave, where it returned


class JudgeDecided(BaseModel):
    verdict: Verdict
    line: int | None  # the flawed line, absent on a clean item
    correct: str | None  # what the flawed line reads in the form itself
    case: SeparatingCase | None


@router.get("/next")
def served(root: Root, user_id: UserId, card: str | None = None) -> JudgedItem:
    cards = CardStore(root).all()
    by_template = owners(cards)
    templates = None
    if card is not None:
        chosen = [one for one in cards if one.slug == card]
        if not chosen:
            raise HTTPException(status_code=404, detail=f"no card {card}")
        templates = {one.id for one in chosen[0].templates}
    item = next_item(
        ItemStore(root).served(),
        JudgementLog(root).for_user(user_id),
        drawn(root, user_id, cards),
        templates=templates,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="no item to judge")
    owner, template = by_template[item.template_id]
    first = template.cases[0]
    return JudgedItem(
        item_id=item.id,
        card_slug=owner.slug,
        card_title=owner.title,
        template_title=template.title,
        asks=first_sentence(template.trigger),
        example=JudgeExample(args=first.args, expected=first.expected),
        lines=item.code.splitlines(),
    )


@router.post("/{item_id}")
def decided(root: Root, user_id: UserId, item_id: str, body: JudgeAnswer) -> JudgeDecided:
    held = ItemStore(root).all()
    item = next((one for one in held if one.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail=f"no item {item_id}")
    try:
        answer = Judgement(
            id=new_id(),
            created_at=datetime.now(UTC),
            user_id=user_id,
            item_id=item_id,
            called_clean=body.called_clean,
            line=body.line,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    JudgementLog(root).append(answer)
    case = (
        None
        if item.clean or item.case_args is None or item.outcome is None
        else SeparatingCase(
            args=item.case_args,
            expected=item.case_expected,
            outcome=item.outcome,
            returned=item.returned,
        )
    )
    # the clean sibling built from the same code holds the line as written
    clean = next(
        (
            one
            for one in held
            if one.clean
            and one.template_id == item.template_id
            and one.form_digest == item.form_digest
        ),
        None,
    )
    correct = (
        clean.code.splitlines()[item.line - 1]
        if clean is not None and item.line is not None
        else None
    )
    return JudgeDecided(verdict=verdict(item, answer), line=item.line, correct=correct, case=case)


def first_sentence(text: str) -> str:
    """Up to the first full stop, marks of emphasis dropped."""
    plain = text.replace("**", "").replace("*", "").replace("`", "")
    head, dot, _ = plain.partition(". ")
    return head + "." if dot else plain


def drawn(root: Root, user_id: str, cards: list[Card]) -> dict[str, Place]:
    return places(cards, {one.card_id for one in CardRunLog(root).all(user_id)})


def owners(cards: list[Card]) -> dict[str, tuple[Card, Template]]:
    return {template.id: (card, template) for card in cards for template in card.templates}
