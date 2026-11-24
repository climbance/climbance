from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from climb.schema.provenance import MachineProvenance


class MatchSource(StrEnum):
    USER = "user"  # the set a machine run is scored against
    GENERATOR = "generator"  # what it was told to write; an assertion, so no provenance
    CLASSIFIER = "classifier"


class MatchHead(BaseModel):
    """A match's verdict without its provenance, for a reader that only asks
    which verdict stands."""

    created_at: datetime
    template_id: str
    solution_id: str
    matched: bool
    source: MatchSource


class TemplateMatch(MachineProvenance):
    """Whether one solution displays one of a card's templates. One record per
    pair — `cli/matcher.md` gives why not a set."""

    id: str
    created_at: datetime
    template_id: str  # minted at card import, as `solution_id` is when the problem lands
    solution_id: str
    matched: bool  # a negative is stored, or every re-run re-tests every non-match
    source: MatchSource
    informed_by: list[str] = Field(
        default_factory=list[str]
    )  # calls its author saw, not provenance

    @model_validator(mode="after")
    def _provenance_matches_source(self) -> TemplateMatch:
        self.check_provenance(self.source is MatchSource.CLASSIFIER)
        return self
