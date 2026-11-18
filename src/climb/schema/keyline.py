"""A key-line item: a template's form with one line blanked, and its choices.
`cli/exercise-items.md` gives the items, and `log.md` the exercise they
serve."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from climb.schema.case import CaseOutcome
from climb.schema.judgement import ItemStatus


class KeyLineChoice(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1)  # the line without its indent
    correct: bool
    change: str | None = None  # what the mutant changed, on a wrong choice
    case_args: list[Any] | None = None
    case_expected: Any = None  # `None` is a value an answer may be
    outcome: CaseOutcome | None = None  # wrong or crashed, never timed out
    returned: Any = None

    @model_validator(mode="after")
    def _a_wrong_choice_names_its_case(self) -> KeyLineChoice:
        wrong = (self.change, self.case_args, self.outcome)
        if self.correct and any(one is not None for one in wrong):
            raise ValueError("the form's own line names no case")
        if not self.correct and any(one is None for one in wrong):
            raise ValueError("a wrong choice names its change and its case")
        if self.outcome is CaseOutcome.TIMEOUT:
            raise ValueError("a wrong line is read off the code, and a timeout is not")
        return self


class KeyLineItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    template_id: str
    form_digest: str = Field(min_length=1)
    code: str = Field(min_length=1)  # the form as shown, its own line in place
    line: int = Field(ge=1)  # the blanked line in `code`, counted from 1
    choices: list[KeyLineChoice] = Field(min_length=3, max_length=4)
    status: ItemStatus = ItemStatus.SERVED

    @model_validator(mode="after")
    def _one_choice_is_the_form(self) -> KeyLineItem:
        if sum(one.correct for one in self.choices) != 1:
            raise ValueError("exactly one choice is the form's own line")
        if len({one.text for one in self.choices}) != len(self.choices):
            raise ValueError("two choices read the same")
        lines = self.code.splitlines()
        if self.line > len(lines):
            raise ValueError(f"line {self.line} past the form's {len(lines)}")
        return self


class Fill(BaseModel):
    """One user's answer to one key-line item: `log.md`, Filling a key line."""

    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    user_id: str = Field(min_length=1)
    item_id: str = Field(min_length=1)
    choice: int = Field(ge=0)  # the picked choice's position in the item


__all__ = ["Fill", "KeyLineChoice", "KeyLineItem"]
