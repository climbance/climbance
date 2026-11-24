from datetime import datetime

from sqlalchemy import func, select

from climb.schema import Solution, SolutionRole
from climb.solutions.table import solutions
from climb.storage import Database, Log


class SolutionLog(Log[Solution]):
    """The solutions a problem carries, in every role."""

    def __init__(self, root: Database) -> None:
        super().__init__(root, solutions, Solution)

    def solutions(self) -> list[Solution]:
        return self.all()

    def landed(self) -> dict[str, datetime]:
        """Each problem's first `created_at`, which landing writes."""
        query = select(solutions.c.problem_id, func.min(solutions.c.created_at)).group_by(
            solutions.c.problem_id
        )
        with self.root.connect() as conn:
            return {problem_id: at for problem_id, at in conn.execute(query)}

    def for_problem(self, problem_id: str, role: SolutionRole | None = None) -> list[Solution]:
        if role is None:
            return self.where(solutions.c.problem_id == problem_id)
        return self.where(solutions.c.problem_id == problem_id, solutions.c.role == role)
