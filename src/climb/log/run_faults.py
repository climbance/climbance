from collections.abc import Callable
from datetime import datetime

from climb.ids import new_id
from climb.log.table import run_faults
from climb.runner import RunnerError
from climb.schema import RunFault, RunKind
from climb.storage import Database, Log


class Faulted(ValueError):
    """The sandbox answered no result for the run, which still counts."""


class RunFaultLog(Log[RunFault]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, run_faults, RunFault)

    def for_user(
        self, user_id: str, *, kind: RunKind | None = None, since: datetime | None = None
    ) -> list[RunFault]:
        conditions = [run_faults.c.user_id == user_id]
        if kind is not None:
            conditions.append(run_faults.c.kind == kind)
        if since is not None:
            conditions.append(run_faults.c.created_at >= since)
        return self.where(*conditions)

    def counted[T](self, user_id: str, kind: RunKind, at: datetime, run: Callable[[], T]) -> T:
        """The run, a fault stored so the caps count it: a solution can end its
        own sandbox, `README.md`, Boundaries."""
        try:
            return run()
        except RunnerError as error:
            self.append(
                RunFault(
                    id=new_id(),
                    created_at=at,
                    user_id=user_id,
                    kind=kind,
                    detail=str(error)[:2000],
                )
            )
            raise Faulted("the sandbox failed on this run, and the run still counts") from error
