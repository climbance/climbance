from datetime import datetime

from sqlalchemy import func, select

from climb.schema import Solution, SolutionHead, SolutionRole
from climb.solutions.table import solutions
from climb.storage import Database, Log


class SolutionLog(Log[Solution]):
    """The solutions a problem carries, in every role."""

    def __init__(self, root: Database) -> None:
        super().__init__(root, solutions, Solution)

    def solutions(self) -> list[Solution]:
        return self.all()

    def heads(self, role: SolutionRole | None = None) -> list[SolutionHead]:
        query = select(solutions.c.id, solutions.c.problem_id, solutions.c.role)
        if role is not None:
            query = query.where(solutions.c.role == role)
        with self.root.connect() as conn:
            return [
                SolutionHead(id=id, problem_id=problem_id, role=role)
                for id, problem_id, role in conn.execute(query.order_by(solutions.c.appended))
            ]

    def canonicals(self) -> list[Solution]:
        return self.where(solutions.c.role == SolutionRole.CANONICAL)

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
