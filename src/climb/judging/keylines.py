"""Key-line items built from the seeded templates: `content.md`, Key-line
items."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from climb.ids import new_id
from climb.judging.build import digest, flaws, rebuild, servable, spread
from climb.schema import Card, KeyLineChoice, KeyLineItem, Template

# a wrong choice per mutant, beside the form's own line: four choices at most
WRONG = 3


def key_lines(template: Template, *, now: datetime) -> list[KeyLineItem]:
    """Up to three items, each blanking a line two mutants or more get wrong."""
    form = servable(template)
    if form is None:
        return []
    lines = form.splitlines()
    wrong: dict[int, dict[str, dict[str, Any]]] = {}
    for flaw in flaws(template, form):
        number: int = flaw["line"]
        code: str = flaw["code"]
        text = code.splitlines()[number - 1].strip()
        if text != lines[number - 1].strip():
            wrong.setdefault(number, {}).setdefault(text, flaw)
    blanked = {number: texts for number, texts in wrong.items() if len(texts) >= 2}
    return [
        KeyLineItem(
            id=new_id(),
            created_at=now,
            template_id=template.id,
            form_digest=digest(template.code),
            code=form,
            line=number,
            choices=[KeyLineChoice(text=lines[number - 1].strip(), correct=True)]
            + [_choice(text, flaw) for text, flaw in list(blanked[number].items())[:WRONG]],
        )
        for number in spread(list(blanked), {number: number for number in blanked})
    ]


def build_key_lines(
    cards: Sequence[Card], held: Sequence[KeyLineItem], *, now: datetime
) -> tuple[list[KeyLineItem], list[str]]:
    return rebuild(cards, held, lambda template: key_lines(template, now=now))


def _choice(text: str, flaw: dict[str, Any]) -> KeyLineChoice:
    return KeyLineChoice(
        text=text,
        correct=False,
        change=flaw["change"],
        case_args=flaw["case_args"],
        case_expected=flaw["case_expected"],
        outcome=flaw["outcome"],
        returned=flaw["returned"],
    )
