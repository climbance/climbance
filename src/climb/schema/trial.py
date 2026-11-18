"""One panel member's solution to one problem: `cli/difficulty/trials.md`."""

from datetime import datetime

from pydantic import Field, model_validator

from climb.schema.case import CaseOutcome
from climb.schema.provenance import MachineProvenance


class Trial(MachineProvenance):
    id: str
    created_at: datetime
    problem_id: str = Field(min_length=1)
    try_number: int = Field(ge=1)  # of this member on this problem
    outcome: CaseOutcome | None = None  # the severest case's; absent where no case ran
    cases_passed: int = Field(ge=0)
    cases_run: int = Field(ge=0)
    cap_ms: int = Field(gt=0)  # the per-case cap that decided any `TIMEOUT`
    runner: str = Field(min_length=1)  # backend and interpreter, opaque; never parsed

    @property
    def solved(self) -> bool:
        return self.outcome is CaseOutcome.PASSED

    @model_validator(mode="after")
    def _counts_match_the_outcome(self) -> Trial:
        """Rejects counts that disagree with the outcome: a pass is every case
        passed, and no case run is no outcome."""
        self.check_provenance(True)
        if self.cases_passed > self.cases_run:
            raise ValueError("a trial passes no more cases than it runs")
        if (self.outcome is None) != (self.cases_run == 0):
            raise ValueError("a trial has an outcome exactly when a case ran")
        if self.solved != (self.cases_run > 0 and self.cases_passed == self.cases_run):
            raise ValueError("a trial passed exactly when every case it ran passed")
        return self
