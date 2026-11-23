"""Judgement items built from the seeded templates: `cli/exercise-items.md`,
Judgement items."""

import ast
import hashlib
import io
import tokenize
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any, Protocol

from climb.cards.check import CAP_MS, passes
from climb.ids import new_id
from climb.mutation import Mutant, mutants, pace
from climb.runner import run
from climb.schema import (
    Card,
    CaseOutcome,
    ItemStatus,
    JudgementItem,
    Template,
    TemplateKind,
)

# the widest line an item shows: the modules' width, wrapped once on a phone
WIDTH = 60
# flawed items per template, beside one clean: a quarter of the items clean
FLAWED = 3


def digest(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def shown(code: str, harness: Sequence[str]) -> str:
    """The code as an item shows it: no comments, no harness, no blank runs."""
    tree = ast.parse(code)
    hidden = _harness_lines(tree, harness)
    comments: dict[int, int] = {}
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        if token.type == tokenize.COMMENT:
            comments[token.start[0]] = token.start[1]
    kept: list[str] = []
    for number, line in enumerate(code.splitlines(), 1):
        if number in hidden:
            continue
        text = line[: comments[number]].rstrip() if number in comments else line.rstrip()
        if text or line.strip() == "":
            kept.append(text)
    lines = [one for index, one in enumerate(kept) if one or (index and kept[index - 1])]
    return "\n".join(lines).strip("\n") + "\n"


def items(template: Template, *, now: datetime) -> list[JudgementItem]:
    """One clean item and up to three flawed, or none where no flaw fits."""
    form = servable(template)
    found = flaws(template, form) if form is not None else []
    if form is None or not found:
        return []
    base: dict[str, Any] = {
        "created_at": now,
        "template_id": template.id,
        "form_digest": digest(template.code),
    }
    clean = JudgementItem.model_validate(base | {"id": new_id(), "code": form, "clean": True})
    return [clean] + [
        JudgementItem.model_validate(base | one | {"id": new_id(), "clean": False})
        for one in _spread(found)
    ]


class Built(Protocol):
    @property
    def id(self) -> str: ...
    @property
    def template_id(self) -> str: ...
    @property
    def form_digest(self) -> str: ...
    @property
    def status(self) -> ItemStatus: ...


def build(
    cards: Sequence[Card], held: Sequence[JudgementItem], *, now: datetime
) -> tuple[list[JudgementItem], list[str]]:
    return rebuild(cards, held, lambda template: items(template, now=now))


def rebuild[T: Built](
    cards: Sequence[Card],
    held: Sequence[T],
    make: Callable[[Template], list[T]],
    current_shape: Callable[[T], bool] = lambda _: True,
) -> tuple[list[T], list[str]]:
    """The items to add and the ids to retire."""
    served = _served(held)
    added: list[T] = []
    retired: list[str] = []
    for template in stale(cards, held, current_shape):
        retired += [one.id for one in served.get(template.id, [])]
        added += make(template)
    return added, retired


def stale[T: Built](
    cards: Sequence[Card], held: Sequence[T], current_shape: Callable[[T], bool] = lambda _: True
) -> list[Template]:
    """The templates a build would rebuild: every one but those already served
    at their current code, in the current shape."""
    served = _served(held)
    return [
        template
        for card in cards
        for template in card.templates
        if not (
            (current := served.get(template.id))
            and all(
                one.form_digest == digest(template.code) and current_shape(one) for one in current
            )
        )
    ]


def _served[T: Built](held: Sequence[T]) -> dict[str, list[T]]:
    served: dict[str, list[T]] = {}
    for one in held:
        if one.status is ItemStatus.SERVED:
            served.setdefault(one.template_id, []).append(one)
    return served


def flaws(template: Template, form: str) -> list[dict[str, Any]]:
    """Each mutant changing one shown line and failing a case, in tree order."""
    args = [case.args for case in template.cases]
    ran = run(template.code, args, cap_ms=CAP_MS)
    cap = pace(max((one.elapsed_ms or 0 for one in ran), default=0), cap_ms=CAP_MS)
    hidden = _harness_lines(ast.parse(template.code), template.harness)
    return [
        flaw
        for one in mutants(template.code)
        if one.line not in hidden and (flaw := _flaw(template, form, one, args, cap))
    ]


def servable(template: Template) -> str | None:
    """The form as shown, where it can make an item at all."""
    if template.kind is not TemplateKind.CODE or not template.cases:
        return None
    form = shown(template.code, template.harness)
    return None if width(form) > WIDTH else form


def spread[T](lines: Sequence[int], picked: dict[int, T]) -> list[T]:
    """Up to `FLAWED` of `picked`, by line, spread over the form."""
    ordered = sorted(lines)
    if len(ordered) <= FLAWED:
        return [picked[line] for line in ordered]
    chosen = {round(index * (len(ordered) - 1) / (FLAWED - 1)) for index in range(FLAWED)}
    return [picked[ordered[index]] for index in sorted(chosen)]


def _flaw(
    template: Template, form: str, mutant: Mutant, args: list[list[Any]], cap: int
) -> dict[str, Any] | None:
    if mutant.span is None or mutant.text is None:
        return None  # a change spanning lines cannot be shown on one
    view = shown(spliced(template.code, mutant.span, mutant.text), template.harness)
    before, after = form.splitlines(), view.splitlines()
    if len(before) != len(after) or width(view) > WIDTH:
        return None
    moved = [number for number, (a, b) in enumerate(zip(before, after, strict=True), 1) if a != b]
    if len(moved) != 1:
        return None
    ran = run(mutant.code, args, cap_ms=cap, stop_early=True)
    for case, one in zip(template.cases, ran, strict=False):
        if passes(one, case.expected, template):
            continue
        outcome = CaseOutcome(str(one.outcome)) if not one.returned else CaseOutcome.WRONG
        if outcome is CaseOutcome.TIMEOUT:
            return None  # a slowdown is not read off the code
        return {
            "code": view,
            "line": moved[0],
            "change": mutant.change,
            "case_args": case.args,
            "case_expected": case.expected,
            "outcome": outcome,
            "returned": one.value if one.returned else None,
        }
    return None


def spliced(code: str, span: tuple[int, int, int], text: str) -> str:
    """The author's code with one node replaced, its formatting kept."""
    number, start, end = span
    lines = code.splitlines(keepends=True)
    # the parser's columns count UTF-8 bytes, not characters
    line = lines[number - 1].encode()
    lines[number - 1] = (line[:start] + text.encode() + line[end:]).decode()
    return "".join(lines)


def _spread(found: list[dict[str, Any]]) -> list[dict[str, Any]]:
    first: dict[int, dict[str, Any]] = {}
    for one in found:
        first.setdefault(one["line"], one)
    return spread(list(first), first)


def _harness_lines(tree: ast.Module, harness: Sequence[str]) -> set[int]:
    lines: set[int] = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef) and node.name in harness:
            start = min([node.lineno, *(one.lineno for one in node.decorator_list)])
            lines.update(range(start, (node.end_lineno or node.lineno) + 1))
    return lines


def width(code: str) -> int:
    return max((len(line) for line in code.splitlines()), default=0)
