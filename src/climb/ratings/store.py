from typing import Any

from sqlalchemy import insert, select

from climb.ratings.table import difficulty_fit_members, difficulty_fits, difficulty_ratings
from climb.schema import DifficultyFit, DifficultyRating
from climb.storage import Database, Log


class RatingLog(Log[DifficultyRating]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, difficulty_ratings, DifficultyRating)

    def ratings(self) -> list[DifficultyRating]:
        return self.all()

    def for_problem(self, problem_id: str) -> list[DifficultyRating]:
        return self.where(difficulty_ratings.c.problem_id == problem_id)


class FitLog:
    """Each fit with the ratings it scored, written in one transaction: a fit
    with half its ratings would stand for problems it never scored."""

    def __init__(self, root: Database) -> None:
        self.root = root

    def append(self, fit: DifficultyFit, ratings: list[DifficultyRating]) -> None:
        if any(one.fit_id != fit.id for one in ratings):
            raise ValueError("a fit stores only the ratings naming it")
        with self.root.begin() as conn:
            conn.execute(insert(difficulty_fits).values(fit.model_dump(exclude={"members"})))
            conn.execute(
                insert(difficulty_fit_members),
                [
                    member.model_dump() | {"fit_id": fit.id, "position": position}
                    for position, member in enumerate(fit.members)
                ],
            )
            if ratings:
                conn.execute(insert(difficulty_ratings), [one.model_dump() for one in ratings])

    def fits(self) -> list[DifficultyFit]:
        with self.root.connect() as conn:
            rows = conn.execute(select(difficulty_fits).order_by(difficulty_fits.c.appended))
            fits = [dict(row) for row in rows.mappings()]
            members: dict[str, list[dict[str, Any]]] = {row["id"]: [] for row in fits}
            held = conn.execute(
                select(difficulty_fit_members).order_by(difficulty_fit_members.c.position)
            ).mappings()
            for one in held:
                members[one["fit_id"]].append(dict(one))
        return [DifficultyFit.model_validate(row | {"members": members[row["id"]]}) for row in fits]
