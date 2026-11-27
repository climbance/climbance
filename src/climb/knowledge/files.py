"""A module's authored files, read as they are: `content-repo/modules.md`."""

import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from climb.knowledge.concepts import derive, read_concepts, rendered


class Bank(BaseModel):
    topic: str
    sub: str
    questions: list[dict[str, Any]]


class ModuleSource(BaseModel):
    slug: str  # the directory's name
    course: dict[str, Any]
    banks: list[Bank]
    graph: dict[str, Any] | None
    certifications: dict[str, Any] | None
    lesson_texts: dict[str, str]  # lesson slug to its Markdown, for the files found
    concepts: dict[str, dict[str, Any]]  # by slug, as authored
    # what reading alone could already tell is wrong: a bank the course does
    # not list, a file that does not parse, a lesson whose file is missing
    unread: list[str]


def read_module(base: Path) -> ModuleSource:
    unread: list[str] = []
    banks: list[Bank] = []
    course = tomllib.loads((base / "course.toml").read_text())
    listed = {(t["slug"], s) for t in course.get("topic", []) for s in t.get("subs", [])}
    for path in sorted((base / "banks").glob("*/*.toml")):
        where = f"{path.parent.name}/{path.stem}"
        if (path.parent.name, path.stem) not in listed:
            unread.append(f"{where}: not in course.toml")
        try:
            raws = tomllib.loads(path.read_text()).get("q", [])
        except tomllib.TOMLDecodeError as error:
            unread.append(f"{where}: {error}")
            continue
        banks.append(Bank(topic=path.parent.name, sub=path.stem, questions=raws))
    _drills(base, banks, listed, unread)
    concepts = read_concepts(base, unread)
    for bank in banks:
        for raw in bank.questions:
            unread += derive(f"{bank.topic}/{bank.sub}", raw, concepts)
    graph = _optional(base / "graph.toml")
    texts: dict[str, str] = {}
    authored: dict[str, dict[str, Any]] = (graph or {}).get("lesson", {})
    for slug, lesson in authored.items():
        path = base / lesson.get("file", "")
        if path.is_file():
            texts[slug] = rendered(slug, path.read_text(), concepts)
        else:
            unread.append(f"lesson {slug}: file {lesson.get('file')} not found")
    return ModuleSource(
        slug=base.name,
        course=course,
        banks=banks,
        graph=graph,
        certifications=_optional(base / "certs.toml"),
        lesson_texts=texts,
        concepts=concepts,
        unread=unread,
    )


def _drills(base: Path, banks: list[Bank], listed: set[tuple[str, str]], unread: list[str]) -> None:
    """Each subtopic's drill items, after its questions:
    `content-repo/ai-drills.md`."""
    by_sub = {(bank.topic, bank.sub): bank for bank in banks}
    for path in sorted((base / "drills").glob("*/*.toml")):
        where = (path.parent.name, path.stem)
        if where not in listed:
            unread.append(f"drills/{'/'.join(where)}: not in course.toml")
        try:
            raws = tomllib.loads(path.read_text()).get("drill", [])
        except tomllib.TOMLDecodeError as error:
            unread.append(f"drills/{'/'.join(where)}: {error}")
            continue
        if where not in by_sub:
            by_sub[where] = Bank(topic=where[0], sub=where[1], questions=[])
            banks.append(by_sub[where])
        by_sub[where].questions.extend(raws)


def _optional(path: Path) -> dict[str, Any] | None:
    return tomllib.loads(path.read_text()) if path.exists() else None
