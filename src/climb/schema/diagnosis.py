from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

from climb.schema.attempt import FailureMode
from climb.schema.provenance import MachineProvenance
from climb.schema.record import AttemptRecord


class Cause(StrEnum):
    """The two-way verdict a diagnosis names: `cli/diagnoser.md`."""

    SLIP = "slip"  # the form held, the fault outside it
    FORM = "form"  # the fault in the form: `gap` or `rust`, which the code cannot split


# the cause each failure mode implies; `speed` and `none` name no fault
IMPLIED: dict[FailureMode, Cause] = {
    FailureMode.SYNTAX: Cause.SLIP,
    FailureMode.GAP: Cause.FORM,
    FailureMode.RUST: Cause.FORM,
}


class Diagnosis(AttemptRecord, MachineProvenance):
    """Why an attempt failed, inferred. The machine counterpart of
    `SelfLabel`."""

    cause: Cause
    evidence: str  # what the verdict cites: a timeout, a compile error

    @model_validator(mode="after")
    def _provenance_required(self) -> Diagnosis:
        """A model wrote every diagnosis, so there is no user arm to exempt."""
        self.check_provenance(True)
        return self


class MutantDiagnosis(MachineProvenance):
    """A diagnosis of a labelled mutant, which is no attempt:
    `cli/diagnoser.md`."""

    id: str
    created_at: datetime
    template_id: str = Field(min_length=1)
    form_digest: str = Field(min_length=1)
    code_hash: str = Field(min_length=1)  # of the mutant's code as the call read it
    cause: Cause
    evidence: str

    @model_validator(mode="after")
    def _provenance_required(self) -> MutantDiagnosis:
        self.check_provenance(True)
        return self
