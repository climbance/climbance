"""A module's authored files, read as they are: `content-repo/modules.md`."""

import tomllib
from difflib import SequenceMatcher
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
        for raw in raws:
            if raw.get("format") == "judge":
                items, problems = expanded(raw)
                by_sub[where].questions.extend(items)
                unread += [
                    f"drills/{'/'.join(where)}:{raw.get('id', '?')}: {one}" for one in problems
                ]
            elif raw.get("format") == "trace":
                by_sub[where].questions.append(traced(raw))
            else:
                by_sub[where].questions.append(raw)


# the artefact's own fields, which none of its items carries
ARTEFACT = {"variant", "check", "lines", "output", "explain"}


def expanded(raw: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """A spot-the-flaw artefact as its items: the clean one, then one per
    variant, each variant's span derived from the two texts."""
    shared = {key: value for key, value in raw.items() if key not in ARTEFACT}
    clean = str(raw.get("lines", "")).strip("\n").splitlines()
    artefact = str(raw.get("id", "?"))
    items = [
        shared
        | {
            "artefact": artefact,
            "lines": clean,
            "output": raw.get("output"),
            "explain": raw.get("explain"),
        }
    ]
    variants: list[dict[str, Any]] = raw.get("variant", [])
    # a quarter of the items stay clean, so calling every one flawed fails
    problems = [] if 1 <= len(variants) <= 3 else ["an artefact takes 1 to 3 variants"]
    for variant in variants:
        lines = str(variant.get("lines", "")).strip("\n").splitlines()
        derived = changed(clean, lines)
        if isinstance(derived, str):
            problems.append(f"variant {variant.get('id', '?')}: {derived}")
            continue
        span, fix = derived
        if list(variant.get("span", [])) != list(span):
            stated = variant.get("span")
            problems.append(f"variant {variant.get('id', '?')}: span {stated}, where it is {span}")
        items.append(
            shared
            | {
                "id": f"{artefact}-{variant.get('id', '?')}",
                "artefact": artefact,
                "lines": lines,
                "output": variant.get("output"),
                "explain": variant.get("explain"),
                "span": list(span),
                "fix": fix,
                "clean_output": raw.get("output"),
            }
        )
    return items, problems


def changed(clean: list[str], variant: list[str]) -> tuple[tuple[int, int], list[str]] | str:
    """The variant's one changed span, 1-based and inclusive, and the clean
    lines it replaces."""
    hunks = [
        op
        for op in SequenceMatcher(a=clean, b=variant, autojunk=False).get_opcodes()
        if op[0] != "equal"
    ]
    if not hunks:
        return "reads as the clean artefact"
    if len(hunks) > 1:
        return "differs in more than one span of lines"
    ((kind, i1, i2, j1, j2),) = hunks
    if kind == "delete":
        return "only deletes lines, leaving no line to tap"
    return (j1 + 1, j2), clean[i1:i2]


def traced(raw: dict[str, Any]) -> dict[str, Any]:
    """A trace item with its steps rendered as the clients draw them, the
    arguments and results kept by the module check alone."""
    rendered = {"steps": raw.get("step", []), "corrected": raw.get("corrected", [])}
    return {key: value for key, value in raw.items() if key != "step"} | {
        key: [step_shown(step) for step in steps] for key, steps in rendered.items()
    }


def step_shown(step: dict[str, Any]) -> dict[str, Any]:
    if "call" not in step:
        return step
    args = ", ".join(f"{name}={value!r}" for name, value in step.get("args", {}).items())
    result = step.get("result")
    shown = {"call": f"{step['call']}({args})"}
    return shown | ({} if result is None else {"result": result_shown(result)})


def result_shown(value: object) -> str:
    return value if isinstance(value, str) else repr(value)


def _optional(path: Path) -> dict[str, Any] | None:
    return tomllib.loads(path.read_text()) if path.exists() else None
