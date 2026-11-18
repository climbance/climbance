"""Where a failed solution's fault lies: `cli/diagnoser.md`."""

import json
from dataclasses import dataclass
from enum import StrEnum

from climb.calls import CallLog, Transport, ask, prompt_hash
from climb.schema import Call, Cause, Configuration

# the classifier's deployment, until `score-diagnosis-per-mode` measures one
MODEL = "google/gemma-4-31b-it"
EFFORT = "medium"
PIN = "coreweave/fp4"
TEMPERATURE: float | None = 0.0
DEFAULT = Configuration(model=MODEL, effort=EFFORT, pin=PIN, temperature=TEMPERATURE)

# a reply is a word and a sentence; the choice sites' cap leaves room to reason
MAX_TOKENS = 8000

SYSTEM = """You read a solution that failed, and say where its fault lies.

A form is the standard shape of a technique, the shape a study card teaches.
You are told which form the problem was written for, where it was written
for one.

Answer `slip` when the solution takes the right approach and its form is
intact, and the fault lies outside the form: a misspelled name, arguments in
the wrong order, setup code or input handling written wrong.

Answer `form` when the fault lies in the approach or in the form itself: the
wrong approach, a piece of the form missing, or a piece of the form written
wrong, such as a bound moving the wrong way or a comparison reversed. A fault
inside the form is `form` even where one character would fix it.

Read the code against what the task asks, and against any evidence given
beside it.

Give the evidence as one sentence naming the line or construct at fault."""

SCHEMA = {
    "type": "object",
    "properties": {
        "cause": {"type": "string", "enum": [one.value for one in Cause]},
        "evidence": {"type": "string"},
    },
    "required": ["cause", "evidence"],
    "additionalProperties": False,
}


class Tool(StrEnum):
    """A piece of evidence the call can be given beyond the baseline:
    `cli/diagnoser.md`."""

    DIVERGENCE = "divergence"  # the first case the solution failed
    FORM_CODE = "form-code"  # the target form's code, on attempts alone


@dataclass(frozen=True)
class Task:
    """What the solution was written to do, as the call is told it, and the
    evidence each tool adds."""

    statement: str  # a problem's statement, or a template's title on a mutant
    form: str | None = None  # the target template's title and trigger, never its code
    failed: str | None = None  # the divergence tool's case, rendered
    form_code: str | None = None


@dataclass(frozen=True)
class Reading:
    cause: Cause
    evidence: str


def prompt(task: Task, code: str) -> str:
    form = ["<form>", task.form, "</form>", ""] if task.form else []
    code_of = ["<form_code>", task.form_code, "</form_code>", ""] if task.form_code else []
    failed = ["", "<failed_case>", task.failed, "</failed_case>"] if task.failed else []
    return "\n".join(
        [
            "<task>",
            task.statement,
            "</task>",
            "",
            *form,
            *code_of,
            "<solution>",
            code,
            "</solution>",
            *failed,
        ]
    )


def request_hash(task: Task, code: str) -> str:
    return prompt_hash(SYSTEM, prompt(task, code))


def diagnose(
    transport: Transport,
    log: CallLog,
    task: Task,
    code: str,
    *,
    configuration: Configuration = DEFAULT,
) -> tuple[Reading | None, Call]:
    """The cause the call named, or `None` where it named none: a refusal or a
    reply cut short. The call is logged either way."""
    call, text = ask(
        transport,
        log,
        system=SYSTEM,
        content=prompt(task, code),
        configuration=configuration,
        schema=SCHEMA,
        max_tokens=MAX_TOKENS,
    )
    if text is None or call.stop_reason == "length":
        return None, call
    reply = json.loads(text)
    return Reading(cause=Cause(reply["cause"]), evidence=reply["evidence"]), call
