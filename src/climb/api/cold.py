"""A cold sitting's routes: served, read and submitted to. Pressing End and
the claim go through the sitting's own routes. `api/rating.md`."""

from fastapi import APIRouter

from climb.api.context import Root, UserId
from climb.api.writes import Begin, Submission
from climb.cold import ColdSeated, ColdSubmitted, read, serve_cold, submit_cold

router = APIRouter(prefix="/cold-sittings")


@router.post("")
def served(root: Root, user_id: UserId, body: Begin | None = None) -> ColdSeated:
    return serve_cold(root, user_id=user_id, device=body.device if body else None)


@router.get("/{sitting_id}")
def seated(root: Root, user_id: UserId, sitting_id: str) -> ColdSeated:
    return read(root, sitting_id, user_id=user_id)


@router.post("/{sitting_id}/submissions")
def submitted(root: Root, user_id: UserId, sitting_id: str, body: Submission) -> ColdSubmitted:
    return submit_cold(root, sitting_id, body.code, user_id=user_id)
