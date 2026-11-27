"""The content as one snapshot, at snapshot format 6: `api/snapshot.md`."""

from typing import Any

from sqlalchemy import Connection, select

from climb.knowledge.diagrams import diagram_of, drawings, fenced, whole
from climb.knowledge.schedule import FSRS
from climb.knowledge.table import lessons, modules, questions, subtopics, topics
from climb.storage import Database

FORMAT = 6
RULES: dict[str, Any] = {
    "fsrs": FSRS,
    "levels": {"0": "Foundation", "1": "Associate", "2": "Professional", "3": "Expert"},
}
# the formats a drill item takes: `content-repo/ai-drills.md`
DRILLS = ("estimate", "metric")
# the order a module carries when its file gives none
DEFAULT_ORDER = 100


def snapshot(root: Database) -> dict[str, Any]:
    with root.connect() as conn:
        live = modules.c.retired_at.is_(None)
        held = conn.execute(
            select(modules).where(live).order_by(modules.c.position, modules.c.slug)
        )
        courses = [_course(conn, dict(row)) for row in held.mappings()]
        drawn = drawings(conn, _sources(courses))
    snap: dict[str, Any] = {"format": FORMAT, "rules": RULES, "courses": courses}
    if drawn:
        # absent without Mermaid, so the snapshot stays at format 6
        snap["diagrams"] = drawn
    return snap


def _sources(courses: list[dict[str, Any]]) -> list[str]:
    found = [
        one
        for course in courses
        for text in course.get("lesson_bodies", {}).values()
        for one in fenced(text)
    ]
    found += [
        one for course in courses for raw in course["questions"] if (one := whole(diagram_of(raw)))
    ]
    return list(dict.fromkeys(found))


def _course(conn: Connection, module: dict[str, Any]) -> dict[str, Any]:
    tree = conn.execute(
        select(
            topics,
            subtopics.c.id.label("sub_id"),
            subtopics.c.slug.label("sub"),
            subtopics.c.title.label("sub_title"),
            subtopics.c.techniques.label("sub_techniques"),
        )
        .join(subtopics, subtopics.c.topic_id == topics.c.id)
        .where(topics.c.module_id == module["id"], topics.c.retired_at.is_(None))
        .where(subtopics.c.retired_at.is_(None))
        .order_by(topics.c.position, subtopics.c.position)
    ).mappings()
    listed: dict[str, dict[str, Any]] = {}
    where: dict[str, tuple[str, str]] = {}  # a subtopic's id to its topic and slug
    for row in tree:
        topic = listed.setdefault(
            row["slug"],
            {"slug": row["slug"], "tier": row["tier"], "title": row["title"], "subs": []},
        )
        topic["subs"].append(row["sub"])
        if row["sub_title"] is not None:
            # absent without a title, so an untitled module stays at format 6
            topic.setdefault("sub_titles", {})[row["sub"]] = row["sub_title"]
        if row["sub_techniques"]:
            topic.setdefault("sub_techniques", {})[row["sub"]] = row["sub_techniques"]
        where[row["sub_id"]] = (row["slug"], row["sub"])
    course: dict[str, Any] = {
        "slug": module["slug"],
        "definition": _definition(module, list(listed.values())),
    }
    served = _questions(conn, module["id"], where)
    course["questions"] = [raw for raw in served if raw.get("format") not in DRILLS]
    if drills := [raw for raw in served if raw.get("format") in DRILLS]:
        # apart from `questions`, which an installed app reads whole
        course["drills"] = drills
    taught = conn.execute(
        select(lessons).where(lessons.c.module_id == module["id"], lessons.c.retired_at.is_(None))
    ).mappings()
    authored = {row["slug"]: dict(row) for row in taught}
    if module["graph"] or authored:
        course["graph"] = {
            **(module["graph"] or {}),
            "lesson": {s: _lesson(r) for s, r in authored.items()},
        }
    if authored:
        course["lesson_bodies"] = {slug: row["text"] for slug, row in authored.items()}
    if module["certifications"]:
        course["certs"] = module["certifications"]
    return course


def _definition(module: dict[str, Any], listed: list[dict[str, Any]]) -> dict[str, Any]:
    definition: dict[str, Any] = {
        "title": module["title"],
        "pass_ratio": module["pass_ratio"],
        "kinds": module["kinds"],
        "code_kinds": module["code_kinds"],
        "topic": listed,
    }
    if module["code_lang"] is not None:
        definition["code_lang"] = module["code_lang"]
    if module["position"] != DEFAULT_ORDER:
        definition["order"] = module["position"]
    return definition


def _questions(
    conn: Connection, module_id: str, where: dict[str, tuple[str, str]]
) -> list[dict[str, Any]]:
    rows = conn.execute(
        select(questions)
        .where(questions.c.module_id == module_id, questions.c.retired_at.is_(None))
        .order_by(questions.c.position)
    ).mappings()
    order = {sub_id: at for at, sub_id in enumerate(where)}
    served = sorted(
        (row for row in rows if row["subtopic_id"] in where),
        key=lambda row: order[row["subtopic_id"]],
    )
    return [_question(dict(row), *where[row["subtopic_id"]]) for row in served]


def _question(row: dict[str, Any], topic: str, sub: str) -> dict[str, Any]:
    raw = {**row["body"], "id": row["slug"], "kind": row["kind"], "level": row["level"]}
    raw |= {"prompt": row["prompt"], "topic": topic, "sub": sub}
    if row["format"] != "choice":
        # the wire's name for the glossary's open question
        raw["format"] = "card" if row["format"] == "open" else row["format"]
    for optional in ("code", "lesson"):
        if row[optional] is not None:
            raw[optional] = row[optional]
    return raw


def _lesson(row: dict[str, Any]) -> dict[str, Any]:
    lesson = {"title": row["title"], "file": f"lessons/{row['slug']}.md"}
    lesson |= {"teaches": row["teaches"], "needs": row["needs"], "pretest": row["pretest"]}
    if row["minutes"] is not None:
        lesson["minutes"] = row["minutes"]
    return lesson
