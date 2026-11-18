"""One user's whole log, read out and erased as one, and the account deleted
with it: `log.md` gives what each holds, and why no other user's record is
touched."""

from typing import Any

from pydantic import BaseModel
from sqlalchemy import Connection, Table, delete, select, text

from climb.calls.table import calls
from climb.knowledge.table import (
    answers,
    certification_exams,
    focuses,
    lesson_marks,
    limit_raises,
    module_orders,
    module_status_changes,
    setting_changes,
    stints,
)
from climb.log.feedback import FeedbackLog
from climb.log.fills import FillLog
from climb.log.judgements import JudgementLog
from climb.log.predictions import PredictionLog
from climb.log.recalls import RecallLog
from climb.log.retirement_requests import RetirementRequestLog
from climb.log.run_faults import RunFaultLog
from climb.log.runs import CardRunLog
from climb.log.sittings import SittingStore
from climb.log.store import AttemptLog
from climb.log.table import (
    app_codes,
    app_tokens,
    attempt_claims,
    attempt_verification_case_results,
    attempt_verifications,
    attempts,
    card_run_probes,
    card_runs,
    diagnoses,
    feedback,
    fills,
    identities,
    invitations,
    judgements,
    predictions,
    recall_attempt_case_results,
    recall_attempts,
    retirement_requests,
    run_faults,
    self_labels,
    sessions,
    sitting_pauses,
    sittings,
    users,
)
from climb.schema import (
    Answer,
    Attempt,
    AttemptClaim,
    AttemptVerification,
    Call,
    CardRun,
    CertificationExam,
    Diagnosis,
    Feedback,
    Fill,
    Focus,
    Judgement,
    LessonMark,
    LimitRaise,
    ModuleOrder,
    ModuleStatusChange,
    Prediction,
    RecallAttempt,
    RetirementRequest,
    RunFault,
    SelfLabel,
    SettingChange,
    Sitting,
    Stint,
)
from climb.storage import Database

# each knowledge table, by the field `UserLog` holds its records in
KNOWLEDGE: dict[str, Table] = {
    "answers": answers,
    "stints": stints,
    "module_status_changes": module_status_changes,
    "focuses": focuses,
    "lesson_marks": lesson_marks,
    "certification_exams": certification_exams,
    "limit_raises": limit_raises,
    "module_orders": module_orders,
    "setting_changes": setting_changes,
}


class UserLog(BaseModel):
    """Every record of one user's log, and the calls a model made about the
    user's code."""

    user_id: str
    sittings: list[Sitting]
    attempts: list[Attempt]
    verifications: list[AttemptVerification]
    claims: list[AttemptClaim]
    self_labels: list[SelfLabel]
    diagnoses: list[Diagnosis]
    judgements: list[Judgement]
    fills: list[Fill]
    predictions: list[Prediction]
    card_runs: list[CardRun]
    recall_attempts: list[RecallAttempt]
    retirement_requests: list[RetirementRequest]
    feedback: list[Feedback]
    run_faults: list[RunFault]
    calls: list[Call]
    # the knowledge log: `api/knowledge-log.md`
    answers: list[Answer]
    stints: list[Stint]
    module_status_changes: list[ModuleStatusChange]
    focuses: list[Focus]
    lesson_marks: list[LessonMark]
    certification_exams: list[CertificationExam]
    limit_raises: list[LimitRaise]
    module_orders: list[ModuleOrder]
    setting_changes: list[SettingChange]


def whole_log(root: Database, user_id: str) -> UserLog:
    log = AttemptLog(root)
    claims = log.claims(user_id)
    diagnosed = log.diagnoses(user_id)
    named = {one.call_id for one in [*claims, *diagnosed] if one.call_id is not None}
    with root.connect() as conn:
        rows = conn.execute(
            select(calls).where(calls.c.id.in_(named)).order_by(calls.c.appended)
        ).mappings()
        called = [Call.model_validate(dict(row)) for row in rows]
    return UserLog.model_validate(
        {
            "user_id": user_id,
            "sittings": SittingStore(root).all(user_id),
            "attempts": log.attempts(user_id),
            "verifications": log.verifications(user_id),
            "claims": claims,
            "self_labels": log.self_labels(user_id),
            "diagnoses": diagnosed,
            "judgements": JudgementLog(root).for_user(user_id),
            "fills": FillLog(root).for_user(user_id),
            "predictions": PredictionLog(root).for_user(user_id),
            "card_runs": CardRunLog(root).all(user_id),
            "recall_attempts": RecallLog(root).all(user_id),
            "retirement_requests": RetirementRequestLog(root).for_user(user_id),
            "feedback": FeedbackLog(root).for_user(user_id),
            "run_faults": RunFaultLog(root).for_user(user_id),
            "calls": called,
            # rows, each validated into the record its field names
            **{name: _knowledge(root, table, user_id) for name, table in KNOWLEDGE.items()},
        }
    )


def _knowledge(root: Database, table: Table, user_id: str) -> list[dict[str, Any]]:
    query = select(table).where(table.c.user_id == user_id).order_by(table.c.appended)
    with root.connect() as conn:
        return [dict(row) for row in conn.execute(query).mappings()]


def erased(root: Database, user_id: str) -> dict[str, int]:
    with root.begin() as conn:
        return _erase(conn, user_id)


def account_deleted(root: Database, user_id: str) -> dict[str, int]:
    """Erases the user's log, then deletes the user, every sign-in and the
    invitations its emails were let in by, in one transaction."""
    with root.begin() as conn:
        counted = _erase(conn, user_id)
        emails = select(identities.c.email).where(identities.c.user_id == user_id)
        for table, where in (
            (invitations, invitations.c.email.in_(emails)),
            (app_codes, app_codes.c.user_id == user_id),
            (app_tokens, app_tokens.c.user_id == user_id),
            (sessions, sessions.c.user_id == user_id),
            (identities, identities.c.user_id == user_id),
            (users, users.c.id == user_id),
        ):
            counted[table.name] = conn.execute(delete(table).where(where)).rowcount
    return counted


def _erase(conn: Connection, user_id: str) -> dict[str, int]:
    """Deletes the user's whole log, and each call a model made about the
    user's code that no other record names. Returns how many rows left each
    table."""
    theirs = select(attempts.c.id).where(attempts.c.user_id == user_id)
    runs = select(attempt_verifications.c.id).where(attempt_verifications.c.attempt_id.in_(theirs))
    held = select(sittings.c.id).where(sittings.c.user_id == user_id)
    started = select(card_runs.c.id).where(card_runs.c.user_id == user_id)
    recalled = select(recall_attempts.c.id).where(recall_attempts.c.user_id == user_id)
    counted: dict[str, int] = {}
    # the one delete the append-only tables let through, and for this
    # transaction alone
    conn.execute(text("SET LOCAL climb.erasing = 'on'"))
    named = set(
        conn.execute(
            select(attempt_claims.c.call_id).where(
                attempt_claims.c.attempt_id.in_(theirs), attempt_claims.c.call_id.is_not(None)
            )
        ).scalars()
    ) | set(
        conn.execute(
            select(diagnoses.c.call_id).where(diagnoses.c.attempt_id.in_(theirs))
        ).scalars()
    )
    # children before the rows they name, since the foreign keys refuse the
    # other order
    for table, where in (
        (
            attempt_verification_case_results,
            attempt_verification_case_results.c.attempt_verification_id.in_(runs),
        ),
        (attempt_verifications, attempt_verifications.c.attempt_id.in_(theirs)),
        (attempt_claims, attempt_claims.c.attempt_id.in_(theirs)),
        (self_labels, self_labels.c.attempt_id.in_(theirs)),
        (diagnoses, diagnoses.c.attempt_id.in_(theirs)),
        (attempts, attempts.c.user_id == user_id),
        (sitting_pauses, sitting_pauses.c.sitting_id.in_(held)),
        (sittings, sittings.c.user_id == user_id),
        (
            recall_attempt_case_results,
            recall_attempt_case_results.c.recall_attempt_id.in_(recalled),
        ),
        (recall_attempts, recall_attempts.c.user_id == user_id),
        (judgements, judgements.c.user_id == user_id),
        (fills, fills.c.user_id == user_id),
        (predictions, predictions.c.user_id == user_id),
        (retirement_requests, retirement_requests.c.user_id == user_id),
        (feedback, feedback.c.user_id == user_id),
        (run_faults, run_faults.c.user_id == user_id),
        (card_run_probes, card_run_probes.c.card_run_id.in_(started)),
        (card_runs, card_runs.c.user_id == user_id),
        *((table, table.c.user_id == user_id) for table in KNOWLEDGE.values()),
    ):
        counted[table.name] = conn.execute(delete(table).where(where)).rowcount
    counted["calls"] = _unnamed_calls(conn, named)
    return counted


def _unnamed_calls(conn: Connection, named: set[str]) -> int:
    # every column the database knows to reference a call, read from its
    # catalog, so a table added later keeps its calls without an edit here
    referencing = conn.execute(
        text(
            "SELECT conrelid::regclass::text, attname FROM pg_constraint"
            " JOIN pg_attribute ON attrelid = conrelid AND attnum = ANY(conkey)"
            " WHERE contype = 'f' AND confrelid = 'calls'::regclass"
        )
    ).all()
    still = " AND ".join(
        f'NOT EXISTS (SELECT 1 FROM "{table}" WHERE "{column}" = calls.id)'
        for table, column in referencing
    )
    return conn.execute(
        text(f"DELETE FROM calls WHERE id = ANY(:named) AND {still}"), {"named": sorted(named)}
    ).rowcount
