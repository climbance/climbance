"""The user's projected contest rating, replayed on every read.
`api/projection.md`."""

from fastapi import APIRouter

from climb.api.context import Root, UserId
from climb.projected import Projected, projected

router = APIRouter()


@router.get("/projection")
def projection(root: Root, user_id: UserId) -> Projected:
    return projected(root, user_id)
