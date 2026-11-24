"""The attention flags: `web-app/pages/author/problems/README.md`,
`## Attention flags`. Computed on every read, never stored."""

import re
from collections.abc import Iterable
from enum import StrEnum

from climb.schema import BANDS, DifficultyRating, Problem, ProblemDifficulty


class AttentionFlag(StrEnum):
    UNTAGGED = "untagged"
    TITLED = "titled"
    UNRATED = "unrated"
    OFF_BAND = "off-band"
    REQUESTED = "requested"


def titled(title: str, codes: Iterable[str]) -> bool:
    words = re.findall(r"[a-z0-9]+", title.lower())
    for code in codes:
        slug = code.split("-")
        if any(words[at : at + len(slug)] == slug for at in range(len(words))):
            return True
    return False


def off_band(rating: DifficultyRating, label: ProblemDifficulty) -> bool:
    # a user's rating stores no deviation, and reads as exact
    deviation = rating.deviation or 0.0
    lows = [low for low, _ in BANDS]
    at = [one for _, one in BANDS].index(label)
    high = lows[at + 1] if at + 1 < len(lows) else float("inf")
    return rating.score < lows[at] - deviation or rating.score >= high + deviation


def attention_flags(
    problem: Problem,
    *,
    generator: ProblemDifficulty | None,
    rating: DifficultyRating | None,
    requests: int,
    codes: Iterable[str],
) -> list[AttentionFlag]:
    """`problem` carries its derived techniques; `generator` is the label the
    stored record holds, before the standing rating replaced it."""
    found: list[AttentionFlag] = []
    if not problem.techniques:
        found.append(AttentionFlag.UNTAGGED)
    if titled(problem.title, codes):
        found.append(AttentionFlag.TITLED)
    if rating is None:
        found.append(AttentionFlag.UNRATED)
    elif generator is not None and off_band(rating, generator):
        found.append(AttentionFlag.OFF_BAND)
    # a request waits while its problem is still served
    if requests and problem.served:
        found.append(AttentionFlag.REQUESTED)
    return found
