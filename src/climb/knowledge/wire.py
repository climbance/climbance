"""Sync lines, the shape a client writes and reads, mapped to this project's
records and back. Content is named by slug on the wire and by id in
the store."""

from typing import Any

from climb.schema.authored import LEVEL_NAMES

# a certification whose scope is the whole module, in a sync line's id
WHOLE = "all"
# the wire's queue modes against the store's: `api/knowledge-sync.md`
WIRE_MODES = {"drill": "filtered"}
STORE_MODES = {ours: theirs for theirs, ours in WIRE_MODES.items()}
EXAM = "exam-L"
CERTIFICATION = "cert-"


class Unknown(Exception):
    """A record naming content the store does not hold. The client drops it."""


def mode_in(mode: str) -> tuple[str, int | None, str | None]:
    """The stint's mode, an exam's level, and a certification exam's id."""
    if mode.startswith(EXAM):
        return "exam", int(mode.removeprefix(EXAM)), None
    if mode.startswith(CERTIFICATION):
        certification = mode.removeprefix(CERTIFICATION)
        level = certification.rpartition("-")[2]
        if level not in LEVEL_NAMES:
            raise Unknown(f"unknown certification {certification}")
        return "exam", LEVEL_NAMES.index(level), certification
    return WIRE_MODES.get(mode, mode), None, None


def mode_out(mode: str, level: int | None, certification: str | None) -> str:
    if certification is not None:
        return f"{CERTIFICATION}{certification}"
    return f"{EXAM}{level}" if mode == "exam" else STORE_MODES.get(mode, mode)


def certification_in(module: str, certification: str) -> tuple[str | None, int]:
    """A wire id `<module>-<scope>-<level name>`, as a topic slug or none for
    the whole module, and a level."""
    scope, _, level = certification.removeprefix(f"{module}-").rpartition("-")
    if level not in LEVEL_NAMES or not scope:
        raise Unknown(f"unknown certification {certification}")
    return (None if scope == WHOLE else scope), LEVEL_NAMES.index(level)


def certification_out(module: str, topic: str | None, level: int) -> str:
    return f"{module}-{topic or WHOLE}-{LEVEL_NAMES[level]}"


def answer_out(row: dict[str, Any]) -> dict[str, Any]:
    """An attempt line, leaving out each optional field that is empty."""
    line: dict[str, Any] = {"course": row["module"], "id": row["question"], "ok": row["correct"]}
    if row["guess"]:
        line["guess"] = True
    if row["grade"] is not None:
        line["grade"] = row["grade"]
    for ticks in ("missed", "traps"):
        if row[ticks]:
            line[ticks] = row[ticks]
    if row["wrong"]:
        line["wrong"] = True
    if row.get("measure") is not None:
        line["measure"] = row["measure"]
    return line
