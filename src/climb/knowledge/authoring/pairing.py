"""The cards read beside a module: the two graphs together, over techniques,
and the cards the module is primary for that no subtopic supports.
`content.md`, Cards and subtopics."""

import json
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from climb.knowledge.check import cycle
from climb.knowledge.files import ModuleSource
from climb.schema import CardSeed, GraphSettings

# an edge between two techniques, and the first record that drew it
type Drawn = dict[tuple[str, str], str]


@dataclass
class Paired:
    errors: list[str] = field(default_factory=list[str])
    unnamed: list[str] = field(default_factory=list[str])  # one line per card


def paired(source: ModuleSource, cards: Path) -> Paired:
    """A cycle through both graphs, as the path of techniques that closes it,
    and each card naming the module as primary whose technique no subtopic of
    the module names."""
    techniques = _techniques(source)
    if not cards.is_dir():
        if any(techniques.values()):
            return Paired([f"no cards at {cards}, so the two graphs cannot be read together"])
        return Paired()
    held: dict[str, CardSeed] = {}
    for path in sorted(cards.glob("*.json")):
        try:
            card = CardSeed.model_validate(json.loads(path.read_text()))
        except (json.JSONDecodeError, ValidationError) as error:
            return Paired([f"{path.name}: unreadable card: {error}"])
        held[card.slug] = card
    named = {one for listed in techniques.values() for one in listed}
    found = Paired(
        unnamed=[
            f"card {card.slug}: no subtopic names {card.technique}"
            for card in held.values()
            if card.module == source.slug and card.technique not in named
        ]
    )
    if not named:
        return found
    drawn: Drawn = {}
    _card_edges(held, drawn)
    _prerequisite_edges(source, techniques, drawn)
    if closed := cycle([(one, to, 0) for one, to in drawn]):
        steps = [f"{one} -> {to} ({drawn[one, to]})" for one, to in pairwise(closed)]
        found.errors.append(
            "cycle across the card graph and the prerequisite graph: " + ", ".join(steps)
        )
    return found


def _techniques(source: ModuleSource) -> dict[str, list[str]]:
    """A malformed `sub_techniques` is the seed's check to refuse, so it names
    none here."""
    found: dict[str, list[str]] = {}
    for topic in source.course.get("topic", []):
        named = topic.get("sub_techniques", {})
        for sub in topic.get("subs", []):
            listed: object = (
                cast(dict[str, Any], named).get(sub) if isinstance(named, dict) else None
            )
            entries = cast(list[object], listed) if isinstance(listed, list) else []
            found[sub] = [one for one in entries if isinstance(one, str)]
    return found


def _card_edges(held: dict[str, CardSeed], drawn: Drawn) -> None:
    """An unknown required card draws no edge: the card check refuses it."""
    for card in held.values():
        for requirement in card.requires:
            required = held.get(requirement.card)
            if required is not None and required.technique != card.technique:
                drawn.setdefault((card.technique, required.technique), f"card {card.slug}")


def _prerequisite_edges(
    source: ModuleSource, techniques: dict[str, list[str]], drawn: Drawn
) -> None:
    authored = {k: v for k, v in (source.graph or {}).items() if k not in ("lesson", "exercise")}
    try:
        graph = GraphSettings.model_validate(authored)
    except ValidationError:
        return  # the seed's check refuses it
    needs: dict[str, list[str]] = {}
    for one, to, _ in graph.edges():
        needs.setdefault(one, []).append(to)
    for sub, own in techniques.items():
        for reached in _reached(sub, needs, techniques):
            for one in own:
                for to in techniques[reached]:
                    if one != to:
                        drawn.setdefault((one, to), f"subtopic {sub} needs {reached}")


def _reached(sub: str, needs: dict[str, list[str]], techniques: dict[str, list[str]]) -> set[str]:
    """The subtopics naming a technique that `sub` needs, passing through every
    subtopic naming none."""
    found: set[str] = set()
    seen: set[str] = set()
    pending = list(needs.get(sub, []))
    while pending:
        at = pending.pop()
        if at in seen:
            continue
        seen.add(at)
        if techniques.get(at):
            found.add(at)
        else:
            pending.extend(needs.get(at, []))
    return found
