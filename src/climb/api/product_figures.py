"""The product page's figures, counted across users on each load:
`web-app/pages/author/product/README.md`."""

from datetime import date, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import (
    ColumnElement,
    Date,
    and_,
    cast,
    func,
    literal,
    select,
    union_all,
)

from climb.knowledge.table import answers
from climb.log.table import (
    Role,
    attempts,
    fills,
    identities,
    invitations,
    judgements,
    recall_attempts,
    sittings,
    users,
)
from climb.storage import Database

PERIOD_DAYS = 30
ACTIVE_DAYS = 7
RETENTION_DAYS = (7, 30)


class ProductDay(BaseModel):
    day: date
    learners: int
    sittings: int
    attempts: int
    answers: int


class Retention(BaseModel):
    after_days: int
    # the users whose first act is at least `after_days` old
    counted: int
    retained: int


class ProductFigures(BaseModel):
    period_days: int
    active_days: int
    invited: int
    signed_in: int
    active: int
    retention: list[Retention]
    # newest first, a row of zeros on a day with no act
    days: list[ProductDay]


def _acts(dev_user: str | None):
    # an answer's `at` is when the client says it was given, not when it synced
    every = union_all(
        select(
            sittings.c.user_id, sittings.c.started_at.label("at"), literal("sitting").label("kind")
        ),
        select(attempts.c.user_id, attempts.c.finished_at, literal("attempt")),
        select(answers.c.user_id, answers.c.at, literal("answer")),
        select(recall_attempts.c.user_id, recall_attempts.c.created_at, literal("recall")),
        select(judgements.c.user_id, judgements.c.created_at, literal("judgement")),
        select(fills.c.user_id, fills.c.created_at, literal("fill")),
    ).subquery("every")
    return select(every).where(_learner(every.c.user_id, dev_user)).cte("acts")


def _learner(user_id: ColumnElement[str], dev_user: str | None) -> ColumnElement[bool]:
    authors = (
        select(identities.c.user_id)
        .join(invitations, invitations.c.email == identities.c.email)
        .where(invitations.c.role == Role.AUTHOR)
    )
    kept = user_id.not_in(authors)
    return and_(kept, user_id != dev_user) if dev_user is not None else kept


def product_figures(root: Database, now: datetime, dev_user: str | None) -> ProductFigures:
    acts = _acts(dev_user)
    today = now.date()
    since = datetime.combine(
        today - timedelta(days=PERIOD_DAYS - 1), datetime.min.time(), now.tzinfo
    )
    day = cast(func.timezone("UTC", acts.c.at), Date).label("day")

    def counted(kind: str) -> ColumnElement[int]:
        return func.count().filter(acts.c.kind == kind)

    per_user = (
        select(func.min(acts.c.at).label("first"), func.max(acts.c.at).label("last"))
        .group_by(acts.c.user_id)
        .subquery()
    )

    def kept(after: int) -> tuple[ColumnElement[int], ColumnElement[int]]:
        old_enough = per_user.c.first <= now - timedelta(days=after)
        again = per_user.c.last >= per_user.c.first + timedelta(days=after)
        return (
            func.count().filter(old_enough),
            func.count().filter(and_(old_enough, again)),
        )

    with root.connect() as conn:
        invited = conn.execute(
            select(func.count()).where(invitations.c.role == Role.LEARNER)
        ).scalar_one()
        signed_in = conn.execute(
            select(func.count()).where(_learner(users.c.id, dev_user))
        ).scalar_one()
        active = conn.execute(
            select(func.count(acts.c.user_id.distinct())).where(
                acts.c.at >= now - timedelta(days=ACTIVE_DAYS)
            )
        ).scalar_one()
        rows = conn.execute(
            select(
                day,
                func.count(acts.c.user_id.distinct()),
                counted("sitting"),
                counted("attempt"),
                counted("answer"),
            )
            .where(acts.c.at >= since)
            .group_by(day)
        ).all()
        retained = conn.execute(select(*(n for after in RETENTION_DAYS for n in kept(after)))).one()

    by_day = {row[0]: tuple(row[1:]) for row in rows}
    return ProductFigures(
        period_days=PERIOD_DAYS,
        active_days=ACTIVE_DAYS,
        invited=invited,
        signed_in=signed_in,
        active=active,
        retention=[
            Retention(after_days=after, counted=retained[2 * i], retained=retained[2 * i + 1])
            for i, after in enumerate(RETENTION_DAYS)
        ],
        days=[_day(today - timedelta(days=n), by_day) for n in range(PERIOD_DAYS)],
    )


def _day(one: date, by_day: dict[date, tuple[int, ...]]) -> ProductDay:
    learners, sat, attempted, answered = by_day.get(one, (0, 0, 0, 0))
    return ProductDay(
        day=one, learners=learners, sittings=sat, attempts=attempted, answers=answered
    )
