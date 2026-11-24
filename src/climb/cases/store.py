from sqlalchemy import func, select

from climb.cases.table import test_cases
from climb.schema import TestCase
from climb.storage import Database, Log


class CaseLog(Log[TestCase]):
    """The cases that decide a problem."""

    def __init__(self, root: Database) -> None:
        super().__init__(root, test_cases, TestCase)

    def cases(self) -> list[TestCase]:
        return self.all()

    def counts(self) -> dict[str, int]:
        """Each problem's count of cases, counted in the store: the cases'
        arguments weigh megabytes together."""
        query = select(test_cases.c.problem_id, func.count()).group_by(test_cases.c.problem_id)
        with self.root.connect() as conn:
            return {problem_id: n for problem_id, n in conn.execute(query)}

    def for_problem(self, problem_id: str) -> list[TestCase]:
        return self.where(test_cases.c.problem_id == problem_id)
