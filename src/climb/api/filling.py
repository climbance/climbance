"""The key-line exercise's routes: an item served without its answer, and a
fill decided. `web-app/pages/cards/key-line/`."""

import random
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from climb.api.context import Root, UserId
from climb.api.judging import JudgeExample, SeparatingCase, drawn, first_sentence, owners
from climb.cards import CardStore
from climb.ids import new_id
from climb.judging import blank, filled, next_item
from climb.keylines import KeyLineStore
from climb.log import FillLog
from climb.schema import Fill

router = APIRouter(prefix="/filling")


class FillChoice(BaseModel):
    choice: int  # the position a fill names it by
    text: str


class FilledItem(BaseModel):
    """An item as the page shows it: no field says which choice is right."""

    item_id: str
    card_slug: str
    card_title: str
    template_title: str
    asks: str
    example: JudgeExample
    lines: list[str]  # the blank's first line holds its indent alone, the rest nothing
    blank: int  # the blank's first line, counted from 1
    blank_end: int  # the blank's last line: a statement may span several
    choices: list[FillChoice]  # shuffled, so a position carries no answer


class FillAnswer(BaseModel):
    choice: int


class FillDecided(BaseModel):
    right: bool
    line: str  # the statement as the form writes it, one line per row of the blank
    case: SeparatingCase | None  # the picked choice's, where it was wrong


@router.get("/next")
def served(root: Root, user_id: UserId, card: str | None = None) -> FilledItem:
    cards = CardStore(root).all()
    templates = None
    if card is not None:
        chosen = [one for one in cards if one.slug == card]
        if not chosen:
            raise HTTPException(status_code=404, detail=f"no card {card}")
        templates = {one.id for one in chosen[0].templates}
    item = next_item(
        KeyLineStore(root).served(),
        FillLog(root).for_user(user_id),
        drawn(root, user_id, cards),
        templates=templates,
    )
    if item is None:
        raise HTTPException(status_code=404, detail="no item to fill")
    owner, template = owners(cards)[item.template_id]
    first = template.cases[0]
    lines = item.code.splitlines()
    top, end = blank(item)
    head = lines[top - 1]
    lines[top - 1 : end] = [head[: len(head) - len(head.lstrip())]] + [""] * (end - top)
    offered = [FillChoice(choice=at, text=one.text) for at, one in enumerate(item.choices)]
    random.shuffle(offered)
    return FilledItem(
        item_id=item.id,
        card_slug=owner.slug,
        card_title=owner.title,
        template_title=template.title,
        asks=first_sentence(template.trigger),
        example=JudgeExample(args=first.args, expected=first.expected),
        lines=lines,
        blank=top,
        blank_end=end,
        choices=offered,
    )


@router.post("/{item_id}")
def decided(root: Root, user_id: UserId, item_id: str, body: FillAnswer) -> FillDecided:
    item = next((one for one in KeyLineStore(root).all() if one.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail=f"no item {item_id}")
    if not 0 <= body.choice < len(item.choices):
        raise HTTPException(status_code=422, detail=f"no choice {body.choice}")
    answer = Fill(
        id=new_id(),
        created_at=datetime.now(UTC),
        user_id=user_id,
        item_id=item_id,
        choice=body.choice,
    )
    FillLog(root).append(answer)
    picked = item.choices[body.choice]
    case = (
        None
        if picked.correct or picked.case_args is None or picked.outcome is None
        else SeparatingCase(
            args=picked.case_args,
            expected=picked.case_expected,
            outcome=picked.outcome,
            returned=picked.returned,
        )
    )
    right = next(one for one in item.choices if one.correct)
    return FillDecided(right=filled(item, answer), line=right.text, case=case)
