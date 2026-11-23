"""The slip mutants: one change to a canonical outside its target form,
`cli/diagnoser.md` `## Slip mutants`."""

import builtins
import difflib
import io
import keyword
import tokenize
from collections.abc import Mapping, Sequence

from climb.judging.build import digest, shown, spliced
from climb.judging.labelled import LabelledMutant
from climb.mutation import mutants, pace
from climb.runner import decide, run
from climb.schema import CaseOutcome, FailureMode, Problem, Template, TestCase
from climb.sitting import DRILL_CAP_MS

_KEPT = frozenset(keyword.kwlist) | frozenset(dir(builtins))
_SKIPPED = frozenset(
    {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENDMARKER,
    }
)
# a header's names and annotations differ between a form and a canonical, and
# carry no change a mutant makes
_HEADERS = ("def ", "async def ", "class ", "@")


def logical_lines(code: str) -> list[tuple[range, str]]:
    """Each logical line's source lines and its shape: its tokens, each name
    numbered in its order on the line, so a renamed line keeps its shape."""
    found: list[tuple[range, str]] = []
    parts: list[str] = []
    names: dict[str, str] = {}
    first = 0
    for token in tokenize.generate_tokens(io.StringIO(code).readline):
        if token.type == tokenize.NEWLINE:
            if parts:
                found.append((range(first, token.start[0] + 1), " ".join(parts)))
            parts, names = [], {}
            continue
        if token.type in _SKIPPED:
            continue
        if not parts:
            first = token.start[0]
        own = token.type == tokenize.NAME and token.string not in _KEPT
        parts.append(names.setdefault(token.string, f"v{len(names)}") if own else token.string)
    return found


def outside(form: str, canonical: str) -> set[int] | None:
    """The canonical's lines outside the form, or `None` where some line of the
    form appears nowhere in the canonical, in order."""
    body = [one for one in logical_lines(form) if not one[1].startswith(_HEADERS)]
    code = [one for one in logical_lines(canonical) if not one[1].startswith(_HEADERS)]
    match = difflib.SequenceMatcher(
        None, [shape for _, shape in body], [shape for _, shape in code], autojunk=False
    )
    blocks = match.get_matching_blocks()
    if sum(size for _, _, size in blocks) < len(body):
        return None  # a form line rewritten here might be the line changed
    inside = {line for _, at, size in blocks for lines, _ in code[at : at + size] for line in lines}
    return {line for lines, _ in code for line in lines} - inside


def slips(
    problem: Problem, template: Template, canonical: str, cases: Sequence[TestCase]
) -> list[LabelledMutant]:
    """Each mutant changing one line outside the form and failing a case."""
    lines = outside(shown(template.code, template.harness), canonical)
    if lines is None:
        return []
    # the separating case times the canonical, and a slip is no slowdown
    kept = [one for one in cases if one.round is not None]
    args = [one.args for one in kept]
    view = shown(canonical, []).splitlines()
    ran = run(canonical, args, cap_ms=DRILL_CAP_MS)
    cap = pace(max((one.elapsed_ms or 0 for one in ran), default=0), cap_ms=DRILL_CAP_MS)
    found: list[LabelledMutant] = []
    for mutant in mutants(canonical):
        if mutant.line not in lines or mutant.span is None or mutant.text is None:
            continue
        code = shown(spliced(canonical, mutant.span, mutant.text), [])
        after = code.splitlines()
        if len(after) != len(view):
            continue
        moved = [n for n, (a, b) in enumerate(zip(view, after, strict=True), 1) if a != b]
        if len(moved) != 1:
            continue
        got = run(mutant.code, args, cap_ms=cap, stop_early=True)
        for case, one in zip(kept, got, strict=False):
            outcome = decide(one, case.expected)
            if outcome is CaseOutcome.PASSED:
                continue
            if outcome is not CaseOutcome.TIMEOUT:  # a slowdown is not read off the code
                found.append(
                    LabelledMutant(
                        template_id=template.id,
                        form_digest=digest(template.code),
                        code=code,
                        line=moved[0],
                        change=mutant.change,
                        operator=mutant.operator,
                        mode=FailureMode.SYNTAX,
                        case_args=case.args,
                        case_expected=case.expected,
                        outcome=outcome,
                        returned=one.value if one.returned else None,
                        problem_id=problem.id,
                    )
                )
            break
    return found


def slip_mutants(
    problems: Sequence[Problem],
    templates: Mapping[str, Template],
    canonicals: Mapping[str, str],
    cases: Mapping[str, Sequence[TestCase]],
) -> list[LabelledMutant]:
    """The slip mutants of every served problem written for a template. A
    change to a line one shape names in several canonicals is kept once."""
    found: dict[tuple[str, str], LabelledMutant] = {}
    for problem in sorted(problems, key=lambda one: one.id):
        template = templates.get(problem.target_template_id or "")
        canonical = canonicals.get(problem.id)
        if not problem.served or template is None or canonical is None:
            continue
        view = shown(canonical, []).splitlines()
        for one in slips(problem, template, canonical, cases.get(problem.id, [])):
            found.setdefault((_shape(view[one.line - 1]), one.change), one)
    return sorted(found.values(), key=lambda one: (one.problem_id or "", one.line, one.change))


def _shape(line: str) -> str:
    try:
        return logical_lines(line.strip() + "\n")[0][1]
    except tokenize.TokenError, IndexError:  # a line a bracket carries over
        return line.strip()
