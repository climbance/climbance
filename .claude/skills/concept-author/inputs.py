"""What a step's session is given in its prompt: the parts of the docs its step
needs and the files it judges, so that it spends no turn reading them."""

import re
import subprocess
import tomllib
from pathlib import Path
from typing import NamedTuple

SKILL = ".claude/skills/concept-author/SKILL.md"
CONCEPTS = "docs/authoring/concepts.md"
RULES = "docs/authoring/rules.md"
# the parts of concepts.md each stage's writer, reviewer and fixer reads
STAGE_CONCEPTS = {
    1: [
        "## The order",
        "## The concept record",
        "## Levels",
        "## Claims about cost",
        "## The stage 1 checklist",
    ],
    2: ["## The concept record", "## Claims about cost", "## Lessons and questions"],
    3: ["## The concept record", "## Claims about cost", "## Lessons and questions"],
}


def section(text: str, heading: str) -> str:
    """The section opening at the line starting with `heading`, to the next
    heading of its level or above."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    level = len(heading) - len(heading.lstrip("#"))
    end = next(
        (i for i in range(start + 1, len(lines)) if re.match(rf"#{{1,{level}}} ", lines[i])),
        len(lines),
    )
    return "\n".join(lines[start:end]).strip()


def before(text: str, marker: str) -> str:
    return text[: text.index(marker)].strip()


def docs(engine: Path, role: str, stage: int) -> list[tuple[str, str]]:
    skill = (engine / SKILL).read_text()
    concepts = (engine / CONCEPTS).read_text()
    rules = (engine / RULES).read_text()
    stages = before(section(concepts, "## Stages"), "1. **Concepts.**")
    parts = [(f"{SKILL} (its opening and roles)", before(skill, "## Stage 1:"))]
    if role == "digest":
        return [*parts, (f"{CONCEPTS} `## Stages` (the approval)", stages)]
    # the same per stage for every role, so a stage shares one cached prefix
    parts.append((f"{SKILL} `## Stage {stage}`", section(skill, f"## Stage {stage}:")))
    parts += [(f"{CONCEPTS} `{h}`", section(concepts, h)) for h in STAGE_CONCEPTS[stage]]
    parts.append((f"{CONCEPTS} `## Stages` (the approval)", stages))
    if stage == 1:
        heads = ["## Facts and execution", "## Concepts"]
        parts.append((f"{RULES} (its opening)", before(rules, "## Facts and execution")))
        parts += [(f"{RULES} `{h}`", section(rules, h)) for h in heads]
    else:
        parts.append((RULES, rules))
    return parts


def notes(module: Path, sub: str) -> list[Path]:
    """The notes moved from the briefs of the cards the subtopic pairs with:
    `content-repo/cards-and-subtopics.md`."""
    course = tomllib.loads((module / "course.toml").read_text())
    named = [
        code
        for topic in course.get("topic", [])
        for code in topic.get("sub_techniques", {}).get(sub, [])
    ]
    return [path for code in named if (path := module / "sources" / f"{code}.md").exists()]


def files(module: Path, topic: str, sub: str, role: str, stage: int) -> list[Path]:
    found = []
    if stage == 1 and role != "digest":
        found += notes(module, sub)
    if role == "digest" or (role == "write" and stage == 1):
        return found
    found.append(module / "concepts" / topic / f"{sub}.toml")
    graph = tomllib.loads((module / "graph.toml").read_text()).get("lesson", {})
    found += [
        module / lesson["file"]
        for lesson in graph.values()
        if any(t.split("@")[0] == sub for t in lesson.get("teaches", []))
    ]
    bank = module / "banks" / topic / f"{sub}.toml"
    if stage == 3 and role != "write" and bank.exists():
        found.append(bank)
    return found


def example(module: Path, sub: str, stage: int) -> tuple[str, str] | None:
    """The opening of a written subtopic's file of the layer a writer writes,
    so that the writer spends no turn finding the format."""
    concepts = sorted(p for p in (module / "concepts").rglob("*.toml") if p.stem != sub)
    if not concepts:
        return None
    other = concepts[0]
    if stage == 2:
        graph = tomllib.loads((module / "graph.toml").read_text()).get("lesson", {})
        files = [
            module / lesson["file"]
            for lesson in graph.values()
            if any(t.split("@")[0] == other.stem for t in lesson.get("teaches", []))
        ]
        if not files:
            return None
        path, keep = files[0], "\n".join(files[0].read_text().splitlines()[:80])
    else:
        path = other if stage == 1 else module / "banks" / other.parent.name / other.name
        if not path.exists():
            return None
        text = path.read_text()
        tables = [m.start() for m in re.finditer(r"^\[\[", text, re.M)]
        keep = text[: tables[3]] if len(tables) > 3 else text
    return (f"the format, from {path} (an example of another subtopic)", keep)


class Given(NamedTuple):
    # the system prompt's tail, the same for every session of a stage
    system: str
    text: str


def block(parts: list[tuple[str, str]]) -> str:
    return "\n\n".join(f"## {name}\n\n````\n{text.strip()}\n````" for name, text in parts)


def given(
    engine: Path, module: Path, topic: str, sub: str, role: str, stage: int, extra: list[Path]
) -> Given:
    # labelled by the module's path: the worktree's differs per subtopic
    claude = (f"modules/{module.name}/CLAUDE.md", (module / "CLAUDE.md").read_text())
    system = (
        "# Docs\n\nThe docs every step of this stage reads, as they stand as the step "
        "starts. They are not files to read again.\n\n"
        + block([*docs(engine, role, stage), claude])
    )
    parts = []
    if role == "write" and (shown := example(module, sub, stage)):
        parts.append(shown)
    for path in [*files(module, topic, sub, role, stage), *extra]:
        if path.exists():
            parts.append((str(path), path.read_text()))
    if role in ("review", "fix"):
        check = subprocess.run(
            ["uv", "run", "climb", "module", "check"]
            + ["--content", str(module.parent), module.name, "--sub", sub],
            cwd=engine,
            capture_output=True,
            text=True,
        )
        parts.append(("the module check, run as this step starts", check.stdout))
    text = (
        "\n\n# Given\n\nThe files your step needs, as they stand as it starts; the docs are "
        "in the system prompt. Read a file again only after you change it, and read another "
        "only when your step needs it.\n\n" + block(parts)
    )
    return Given(system, text)
