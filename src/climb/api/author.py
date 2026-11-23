"""The routes the author pages read: `web-app/pages/author/README.md`. The
router's dependency guards every route on it, so a route added here needs no
check of its own."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from climb.api.context import author_id

router = APIRouter(prefix="/author", dependencies=[Depends(author_id)])

# the author pages the engine serves, each the last segment of its path
PAGES: list[str] = []


class AuthorArea(BaseModel):
    pages: list[str]


@router.get("")
def area() -> AuthorArea:
    return AuthorArea(pages=PAGES)
