"""Key-line items built from the seeded templates: `content.md`, Key-line
items."""

import io
import tokenize
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from climb.ids import new_id
from climb.judging.build import digest, flaws, rebuild, servable, spread
from climb.schema import Card, KeyLineChoice, KeyLineItem, Template

# a wrong choice per mutant, beside the form's own line: four choices at most
WRONG = 3


def key_lines(template: Template, *, now: datetime) -> list[KeyLineItem]:
    """Up to three items, each blanking a statement two mutants get wrong."""
    form = servable(template)
    if form is None:
        return []
    spans = statements(form)
    wrong: dict[int, dict[str, dict[str, Any]]] = {}
    for flaw in flaws(template, form):
        first, last = spans[flaw["line"]]
        text = _text(flaw["code"], first, last)
        if text != _text(form, first, last):
            wrong.setdefault(first, {}).setdefault(text, flaw)
    blanked = {number: texts for number, texts in wrong.items() if len(texts) >= 2}
    return [
        KeyLineItem(
            id=new_id(),
            created_at=now,
            template_id=template.id,
            form_digest=digest(template.code),
            code=form,
            line=number,
            choices=[KeyLineChoice(text=_text(form, *spans[number]), correct=True)]
            + [_choice(text, flaw) for text, flaw in list(blanked[number].items())[:WRONG]],
        )
        for number in spread(list(blanked), {number: number for number in blanked})
    ]


def build_key_lines(
    cards: Sequence[Card], held: Sequence[KeyLineItem], *, now: datetime
) -> tuple[list[KeyLineItem], list[str]]:
    return rebuild(cards, held, lambda template: key_lines(template, now=now), whole)


def statements(code: str) -> dict[int, tuple[int, int]]:
    """Each line's statement, as its first and last line: one logical line."""
    spans: dict[int, tuple[int, int]] = {}
    first: int | None = None
    skipped = (tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT)
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        if first is None and token.type not in (*skipped, tokenize.ENDMARKER):
            first = token.start[0]
        if token.type == tokenize.NEWLINE and first is not None:
            last = token.start[0]
            spans |= {number: (first, last) for number in range(first, last + 1)}
            first = None
    return spans


def blank(item: KeyLineItem) -> tuple[int, int]:
    return statements(item.code).get(item.line, (item.line, item.line))


def filled_in(item: KeyLineItem, text: str) -> str:
    """The item's code with `text` in its blank, under the blank's indent."""
    first, last = blank(item)
    lines = item.code.splitlines()
    head = lines[first - 1]
    indent = head[: len(head) - len(head.lstrip())]
    lines[first - 1 : last] = [indent + one for one in text.splitlines()]
    return "\n".join(lines) + "\n"


def whole(item: KeyLineItem) -> bool:
    """Whether the item blanks a whole statement, as older items did not."""
    first, last = blank(item)
    return first == item.line and all(
        len(one.text.splitlines()) == last - first + 1 for one in item.choices
    )


def _text(code: str, first: int, last: int) -> str:
    """A statement's lines without the indent of its first."""
    lines = code.splitlines()[first - 1 : last]
    indent = len(lines[0]) - len(lines[0].lstrip())
    return "\n".join(one[min(indent, len(one) - len(one.lstrip())) :].rstrip() for one in lines)


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
