from collections import defaultdict

from sqlalchemy import ColumnElement, insert, select

from climb.ratings.table import (
    difficulty_corrections,
    difficulty_draws,
    difficulty_rating_draws,
    difficulty_ratings,
)
from climb.schema import DifficultyCorrection, DifficultyDraw, DifficultyRating
from climb.storage import Database, Log


class RatingLog(Log[DifficultyRating]):
    """Each rating with the links to its draws, written in one transaction: a
    judge rating without them names no evidence."""

    def __init__(self, root: Database) -> None:
        super().__init__(root, difficulty_ratings, DifficultyRating)

    def append(self, record: DifficultyRating) -> None:
        with self.root.begin() as conn:
            conn.execute(insert(difficulty_ratings).values(record.model_dump(exclude={"draw_ids"})))
            if record.draw_ids:
                conn.execute(
                    insert(difficulty_rating_draws),
                    [
                        {"rating_id": record.id, "position": position, "draw_id": draw_id}
                        for position, draw_id in enumerate(record.draw_ids)
                    ],
                )

    def where(self, *conditions: ColumnElement[bool]) -> list[DifficultyRating]:
        query = select(difficulty_ratings).where(*conditions)
        with self.root.connect() as conn:
            rows = [
                dict(row)
                for row in conn.execute(query.order_by(difficulty_ratings.c.appended)).mappings()
            ]
            linked: dict[str, list[str]] = defaultdict(list)
            links = select(difficulty_rating_draws).where(
                difficulty_rating_draws.c.rating_id.in_([row["id"] for row in rows])
            )
            for link in conn.execute(
                links.order_by(
                    difficulty_rating_draws.c.rating_id, difficulty_rating_draws.c.position
                )
            ).mappings():
                linked[link["rating_id"]].append(link["draw_id"])
        return [
            DifficultyRating.model_validate(row | {"draw_ids": linked[row["id"]]}) for row in rows
        ]

    def ratings(self) -> list[DifficultyRating]:
        return self.all()

    def for_problem(self, problem_id: str) -> list[DifficultyRating]:
        return self.where(difficulty_ratings.c.problem_id == problem_id)


class DrawLog(Log[DifficultyDraw]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, difficulty_draws, DifficultyDraw)


class CorrectionLog(Log[DifficultyCorrection]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, difficulty_corrections, DifficultyCorrection)
