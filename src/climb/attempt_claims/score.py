"""The classifier scored against the user's own claims, per technique."""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

from climb.attempt_claims.run import Failed
from climb.schema import Call, Configuration
from climb.scorer import Agreement, agreement


class Score(Agreement):
    # Of `undecided`, those cut short by the token cap rather than declined.
    exhausted: int = 0
    failed: list[Failed] = Field(default_factory=list[Failed])
    read: int = 0
    reused: int = 0
    undecided: int = 0
    aborted: bool = False
    # A claim stored before the price was recorded carries none, so a column
    # reports the mean over `costed`.
    cost: float = 0.0
    costed: int = 0
    # Joined from the calls: a claim carries no token counts.
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    tokened: int = 0  # claims whose call reported a count
    reasoned: int = 0  # of those, the ones reporting the reasoning split
    # The answering request alone, never what the caller waited: the difference
    # is the endpoint's backoff. The slowest sits beside the mean, which hides
    # an occasional stall.
    request_ms: int = 0
    slowest_ms: int = 0
    timed: int = 0


class ConfigurationScore(BaseModel):
    configuration: Configuration
    score: Score


class Split(BaseModel):
    """One attempt the configurations read differently from each other, as
    distinct from a `Disagreement`, which is with the user."""

    attempt_id: str
    user: list[str]
    verdicts: list[list[str]]  # aligned with `Comparison.scores`


class Comparison(BaseModel):
    """What each configuration read the eval set as. `common` is the attempts
    every configuration decided; `eval_set` is what was there to read."""

    eval_set: int = 0
    common: int = 0
    scores: list[ConfigurationScore] = []
    splits: list[Split] = []


def score(
    truth: Mapping[str, Sequence[str]],
    machine: Mapping[str, Sequence[str]],
    candidates: Mapping[str, Sequence[str]] | None = None,
) -> Score:
    return Score(**vars(agreement(truth, machine, candidates)))


def spent(scored: Score, calls: Sequence[Call]) -> None:
    """Counted over the calls that reported, never over the claims. The
    reasoning split and the timing each have their own denominator."""
    for call in calls:
        # An empty verdict has two causes and the claim cannot tell them apart,
        # since both name no technique. The call can, so it is counted here.
        scored.exhausted += call.stop_reason == "length"
        if call.request_ms is not None:
            scored.request_ms += call.request_ms
            scored.slowest_ms = max(scored.slowest_ms, call.request_ms)
            scored.timed += 1
        if call.input_tokens is None or call.output_tokens is None:
            continue
        scored.input_tokens += call.input_tokens
        scored.output_tokens += call.output_tokens
        scored.tokened += 1
        if call.reasoning_tokens is not None:
            scored.reasoning_tokens += call.reasoning_tokens
            scored.reasoned += 1
