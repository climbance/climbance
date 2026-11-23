"""The user's measured rating, replayed on every read. `api/rating.md`."""

from fastapi import APIRouter

from climb.api.context import Root, UserId
from climb.measured import Measured, measured

router = APIRouter()


@router.get("/rating")
def rating(root: Root, user_id: UserId) -> Measured:
    return measured(root, user_id)
