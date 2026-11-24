"""Rule 24: a `text` fence holds a drawing, and a drawing sits in one. Rule
25: a line of code fits a phone."""

import re

from climb.knowledge.authoring.course import Course, Report, where
from climb.knowledge.authoring.lessons import DIAGRAM
from climb.knowledge.authoring.tools import transcript

FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.S | re.M)
# a layout: columns aligned by spaces, arrows, an underline, an ordering
DRAWN = re.compile(DIAGRAM.pattern + r"|\S {2,}\S|->|[→←⇒▲▼✓✗]|\|=|[~^]{3}| < .* < ", re.M)
WIDE = 60
# a module written by concept holds a question's code to what a phone shows
NARROW = 40
LONGEST = 12
BOX = re.compile(r"[─│┌┐└┘├┤┬┴┼═║╔╗╚╝╭╮╰╯]")
# a tool's own output may hold them, as `uv tree` prints
HOLDS_BOX = ("text", "output", "console")


def _line(text: str, at: int) -> str:
    return f"line {text.count(chr(10), 0, at) + 1}"


def text_fences(course: Course, report: Report) -> None:
    for slug, text in course.lessons.items():
        for m in FENCE.finditer(text):
            if m[1] == "text" and not DRAWN.search(m[2]):
                report.warn(
                    24,
                    f"lessons/{slug}.md {_line(text, m.start())}",
                    "a text block draws nothing: fence output as `output`",
                )


def box_drawing(course: Course, report: Report) -> None:
    for slug, text in course.lessons.items():
        fences = list(FENCE.finditer(text))
        if m := _in_prose(text, fences):
            at = f"lessons/{slug}.md {_line(text, m.start())} of the prose"
            report.error(24, at, _boxed(m[0]))
        for f in fences:
            if f[1] not in HOLDS_BOX and (m := BOX.search(f[2])):
                report.error(24, f"lessons/{slug}.md {_line(text, f.start())}", _boxed(m[0]))
    for q in course.questions:
        detail = q.get("detail", {})
        for name, value in (
            ("prompt", q.get("prompt")),
            ("code", q.get("code")),
            ("example", detail.get("example")),
            ("mechanism", detail.get("mechanism")),
        ):
            if isinstance(value, str) and (m := BOX.search(value)):
                report.error(24, f"{where(q)} {name}", _boxed(m[0]))


def _in_prose(text: str, fences: list[re.Match[str]]) -> re.Match[str] | None:
    spans = [(f.start(), f.end()) for f in fences]
    prose = (m for m in BOX.finditer(text) if not any(a <= m.start() < b for a, b in spans))
    return next(prose, None)


def _boxed(char: str) -> str:
    return f"{char!r} draws outside a `text` block: a structure is Mermaid, a table is markdown"


def _wide(code: str, limit: int = WIDE) -> str | None:
    over = [len(line) for line in code.splitlines() if len(line) > limit]
    if not over:
        return None
    lines = "line" if len(over) == 1 else "lines"
    return f"{len(over)} {lines} over {limit} characters, the longest {max(over)}"


def _typed(lang: str, block: str) -> tuple[str, str]:
    """A fence as the lines a reader types and the lines a tool printed."""
    if lang == "output":
        return "", block
    if lang != "console":
        return block, ""
    typed: list[str] = []
    printed: list[str] = []
    for command, shown in transcript(block):
        typed.append("$ " + command)
        (typed if command.startswith("cat ") else printed).extend(shown)
    return "\n".join(typed), "\n".join(printed)


def widths(course: Course, report: Report) -> None:
    for q in course.questions:
        for name, code in (
            ("code", q.get("code")),
            ("example", q.get("detail", {}).get("example")),
        ):
            if not isinstance(code, str):
                continue
            if found := _wide(code):
                report.error(25, f"{where(q)} {name}", found)
            elif course.concepts and (found := _wide(code, NARROW)):
                report.warn(25, f"{where(q)} {name}", found)
        lines = len(str(q.get("code", "")).strip().splitlines())
        if course.concepts and lines > LONGEST:
            report.warn(25, f"{where(q)} code", f"{lines} lines, over {LONGEST}")
    # a fence naming a language or `output` wraps; a `text` one is a drawing,
    # and a `mermaid` one is drawn to the screen's width
    for slug, text in course.lessons.items():
        for m in FENCE.finditer(text):
            if not m[1] or m[1] in ("text", "mermaid"):
                continue
            at = f"lessons/{slug}.md {_line(text, m.start())}"
            typed, printed = _typed(m[1], m[2])
            if found := _wide(typed):
                report.error(25, at, found)
            # a tool's own text is quoted whole, so it is only warned
            if found := _wide(printed):
                report.warn(25, at, f"printed: {found}")
