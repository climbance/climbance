"""The authored structure a content row holds as JSONB, typed so the seed
refuses a malformed one: `database/README.md`."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

LETTERS = "ABCDEFGH"
LEVELS = (0, 1, 2, 3)
LEVEL_NAMES = ("foundation", "associate", "professional", "expert")

Text = Annotated[str, StringConstraints(strip_whitespace=False, min_length=1, pattern=r"\S")]


class Authored(BaseModel):
    # a field the format does not know is a typo the seed would store unread
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Detail(Authored):
    """How a question's answer works, shown on request after an answer."""

    mechanism: Text
    example: Text | None = None
    # six: a module written by concept derives them from its misconceptions
    pitfalls: list[Text] | None = Field(default=None, min_length=1, max_length=6)
    versions: Text | None = None
    diagram: Text | None = None


class ChoiceBody(Authored):
    choices: list[str]
    answer: list[str]  # letters into `choices`, more than one for a multi-select
    why: list[str]  # one line per choice, in the same order
    explain: str
    detail: Detail
    # a module written by concept: the concept the question tests, and each
    # wrong choice's letter to the misconception it embodies, by its id
    concept: str | None = None
    misconception: dict[str, str] | None = None
    # derived: each of those letters to its misconception's text
    misconception_text: dict[str, str] | None = None

    @model_validator(mode="after")
    def _choices_and_their_answer(self) -> ChoiceBody:
        n = len(self.choices)
        if not 3 <= n <= len(LETTERS):
            raise ValueError(f"{n} choices")
        if len(self.why) != n:
            raise ValueError(f"{len(self.why)} why for {n} choices")
        answer = self.answer
        if (
            not answer
            or len(set(answer)) != len(answer)
            or any(a not in LETTERS[:n] for a in answer)
        ):
            raise ValueError(f"bad answer {answer!r}")
        return self


class ShortBody(Authored):
    accept: list[str]  # the first is canonical
    case: bool = False
    explain: str
    detail: Detail
    concept: str | None = None

    @model_validator(mode="after")
    def _something_accepted(self) -> ShortBody:
        if not self.accept:
            raise ValueError("empty accept")
        return self


class OpenBody(Authored):
    """An open question's key and its traps."""

    key: list[Text]
    traps: list[Text] = Field(default_factory=list[str])
    explain: str | None = None
    detail: Detail | None = None
    key_detail: list[Text] | None = None
    traps_detail: list[Text] | None = None
    concept: str | None = None

    @model_validator(mode="after")
    def _points_and_their_details(self) -> OpenBody:
        if not 2 <= len(self.key) <= 6:
            raise ValueError("key must be a list of 2-6 non-empty points")
        if len(self.traps) > 3:
            raise ValueError("traps must be a list of 0-3 non-empty strings")
        for name, details, parent in (
            ("key_detail", self.key_detail, self.key),
            ("traps_detail", self.traps_detail, self.traps),
        ):
            if details is None:
                continue
            if len(details) != len(parent):
                raise ValueError(f"{name} must have one non-empty string per item ({len(parent)})")
            if any(len(one.strip().splitlines()) > 3 for one in details):
                raise ValueError(f"{name} items must be at most 3 lines")
        return self


# the names an estimate's `compute` is given besides its own
ESTIMATE_NAMES = ("sent", "received", "tokens")


class Given(Authored):
    """One number or name an estimate states, shown as its label and value."""

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    label: Text
    value: float | str


class EstimateBody(Authored):
    """An estimate drill: `content-repo/ai-drills.md`."""

    sent: Text | None = None  # the prompt the call sends
    received: Text | None = None  # the answer it returns
    given: list[Given]
    # prints the working, a line each, then the key as the last line
    compute: Text
    working: list[Text]
    computed: float = Field(gt=0)  # the key, as `compute` printed it
    factor: float = Field(gt=1)
    unit: Text
    explain: str
    detail: Detail | None = None
    concept: str | None = None

    @model_validator(mode="after")
    def _names_once(self) -> EstimateBody:
        names = [one.name for one in self.given]
        if len(set(names)) < len(names):
            raise ValueError("given names a value twice")
        if taken := sorted(set(names) & set(ESTIMATE_NAMES)):
            raise ValueError(f"given takes the reserved name {taken[0]}")
        return self


class Candidate(Authored):
    """One metric a pick-the-metric item offers, from the module's library."""

    metric: str = Field(pattern=r"^[a-z][a-z0-9_]*$")  # a function in metrics.py
    label: Text
    params: dict[str, Any] = Field(default_factory=dict[str, Any])


class MetricBody(Authored):
    """A pick-the-metric drill: `content-repo/ai-drills.md`. Its key is the
    one candidate ranking the two systems as `utility` does."""

    inputs: list[Text] | None = None  # shown beside each case, where it helps
    expected: list[Any]
    a: list[Any]  # system A's output on each case
    b: list[Any]
    candidates: list[Candidate] = Field(min_length=2, max_length=5)
    # defines `utility(outputs, expected)`, the goal's own score
    utility: Text
    # as the module check computed them: each candidate's, and the goal's
    scores: list[tuple[float, float]]
    goal: tuple[float, float]
    explain: str
    detail: Detail | None = None
    concept: str | None = None

    @model_validator(mode="after")
    def _one_candidate_ranks_as_the_goal(self) -> MetricBody:
        cases = len(self.expected)
        if not 1 <= cases <= MAX_CASES:
            raise ValueError(f"expected holds 1 to {MAX_CASES} cases")
        for name, values in (("inputs", self.inputs), ("a", self.a), ("b", self.b)):
            if values is not None and len(values) != cases:
                raise ValueError(f"{name} holds {len(values)} cases, where expected holds {cases}")
        if len(self.scores) != len(self.candidates):
            raise ValueError("scores holds one pair per candidate")
        if self.goal[0] == self.goal[1]:
            raise ValueError("the goal ties the two systems, so no metric is right")
        if len(agreeing(self.scores, self.goal)) != 1:
            raise ValueError("exactly one candidate must rank the systems as the goal does")
        return self


# a phone shows every case as a row
MAX_CASES = 12


def agreeing(scores: list[tuple[float, float]], goal: tuple[float, float]) -> list[int]:
    """The candidates putting first the system the goal puts first. A tie
    decides nothing, so it agrees with no goal."""
    ahead = goal[0] > goal[1]
    return [i for i, (a, b) in enumerate(scores) if a != b and (a > b) == ahead]


# a tap lands on one line of a phone's screen: `content-repo/ai-drills.md`
TAP_WIDTH = 60


class JudgeBody(Authored):
    """One spot-the-flaw item: an artefact, clean or one variant of it,
    expanded at read: `content-repo/ai-drills.md`."""

    artefact: str  # the authored artefact's id, shared by its clean and its variants
    lines: list[str] = Field(min_length=1)
    input: Text  # the call the witness runs, as shown
    output: Text  # what these lines gave on it, as the module check computed it
    # a flawed item's alone: its span, the clean lines there, the clean output
    span: tuple[int, int] | None = None
    fix: list[str] | None = None
    clean_output: Text | None = None
    explain: str
    detail: Detail | None = None
    concept: str | None = None

    @model_validator(mode="after")
    def _a_span_on_its_lines(self) -> JudgeBody:
        if wide := [i + 1 for i, line in enumerate(self.lines) if len(line) > TAP_WIDTH]:
            raise ValueError(f"line {wide[0]} is wider than {TAP_WIDTH} characters")
        flawed = (self.span, self.fix, self.clean_output)
        if any(one is None for one in flawed) != all(one is None for one in flawed):
            raise ValueError("a flawed item states its span, its fix and the clean output together")
        if self.span is not None and not 1 <= self.span[0] <= self.span[1] <= len(self.lines):
            raise ValueError(f"span {list(self.span)} is not within the {len(self.lines)} lines")
        return self


class TraceStep(Authored):
    """One step of an agent's run, as the reader renders it: a message, or a
    tool call beside its result."""

    say: Text | None = None
    call: Text | None = None  # `name(arg=value)`
    result: str | None = None  # the environment's, never a tap's key

    @model_validator(mode="after")
    def _a_message_or_a_call(self) -> TraceStep:
        if (self.say is None) == (self.call is None):
            raise ValueError("a step is a message or a call")
        if (self.call is None) != (self.result is None):
            raise ValueError("a call states its result, and a message none")
        return self

    def lines(self) -> list[str]:
        if self.call is None:
            return []  # a message is prose, which a client wraps
        return [self.call, *str(self.result).splitlines()]


class TraceBody(Authored):
    """One read-the-trace item: an agent's failed run and its first wrong step:
    `content-repo/ai-drills.md`."""

    environment: Text  # the scripted environment both runs were replayed in
    steps: list[TraceStep] = Field(min_length=2)
    k: int = Field(ge=1)  # the first wrong step, 1-based
    corrected: list[TraceStep] = Field(min_length=1)  # the corrected run from `k` on
    end_state: Text  # the environment's state after the failed run
    corrected_end_state: Text
    explain: str
    model: str | None = None  # the `model@pin` that wrote the trace, as provenance
    detail: Detail | None = None
    concept: str | None = None

    @model_validator(mode="after")
    def _a_key_step_the_runs_differ_at(self) -> TraceBody:
        if self.k > len(self.steps):
            raise ValueError(f"k {self.k} is past the {len(self.steps)} steps")
        if self.corrected[0] == self.steps[self.k - 1]:
            raise ValueError(f"the corrected run repeats step {self.k}, so it is not the wrong one")
        for n, step in enumerate([*self.steps, *self.corrected], 1):
            if any(len(line) > TAP_WIDTH for line in step.lines()):
                raise ValueError(f"step {n} holds a line wider than {TAP_WIDTH} characters")
        return self


type Body = ChoiceBody | ShortBody | OpenBody | EstimateBody | MetricBody | JudgeBody | TraceBody


class Edge(Authored):
    needs: str = Field(alias="from")  # the subtopic that needs
    to: str
    offset: int = Field(default=0, ge=0)


class GraphSettings(Authored):
    """A module's prerequisite graph. Its lessons are rows of their own."""

    format: Literal[1, 2] = 1
    match_up_to: int = Field(default=1, ge=0, le=3)
    needs: dict[str, list[str]] = Field(default_factory=dict[str, list[str]])
    edge: list[Edge] = Field(default_factory=list[Edge])

    def edges(self) -> list[tuple[str, str, int]]:
        return [(f, to, 0) for f, tos in self.needs.items() for to in tos] + [
            (one.needs, one.to, one.offset) for one in self.edge
        ]


class Exam(Authored):
    size: int | None = Field(default=None, ge=1)
    share: float | None = Field(default=None, alias="pass", gt=0, le=1)


class Retention(Authored):
    stability_days: float | None = Field(default=None, gt=0)
    share: float | None = Field(default=None, gt=0, le=1)


class CertificationRule(Authored):
    """Every field optional: a scope's rule overrides only what it names."""

    exam: Exam | None = None
    retention: Retention | None = None
    coverage_ratio: float | None = Field(default=None, gt=0, le=1)
    levels: list[Literal[0, 1, 2, 3]] | None = None
    min_pool_ratio: float | None = Field(default=None, ge=0)
    require_exam: bool | None = None
    lapse: bool | None = None


class ScopeRule(CertificationRule):
    """A scope's rule, and its rule per level, keyed by level name."""

    foundation: CertificationRule | None = None
    associate: CertificationRule | None = None
    professional: CertificationRule | None = None
    expert: CertificationRule | None = None


class CertificationEdge(Authored):
    needs: str = Field(alias="from")
    to: str


class CertificationSettings(Authored):
    format: Literal[1] = 1
    defaults: CertificationRule = Field(default_factory=CertificationRule)
    scope: dict[str, ScopeRule] = Field(default_factory=dict[str, ScopeRule])
    edge: list[CertificationEdge] = Field(default_factory=list[CertificationEdge])
    unedge: list[CertificationEdge] = Field(default_factory=list[CertificationEdge])
