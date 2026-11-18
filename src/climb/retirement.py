"""A user's request that a problem be retired. The author reads it and retires
the problem by hand: `api/problems.md`."""

from datetime import datetime

from climb.ids import new_id
from climb.log import RetirementRequestLog
from climb.problems import ProblemStore
from climb.schema import RetirementReason, RetirementRequest
from climb.sitting import Missing, Refused


def requested(
    problems: ProblemStore,
    requests: RetirementRequestLog,
    problem_id: str,
    *,
    user_id: str,
    reason: RetirementReason,
    note: str,
    now: datetime,
) -> RetirementRequest:
    problem = problems.get(problem_id)
    if problem is None:
        raise Missing(f"no problem {problem_id}")
    if not problem.served:
        raise Refused(f"problem {problem_id} is already {problem.status}")
    one = RetirementRequest(
        id=new_id(),
        created_at=now,
        user_id=user_id,
        problem_id=problem_id,
        reason=reason,
        note=note,
    )
    requests.append(one)
    return one
