"""The routes the author pages read: `web-app/pages/author/README.md`. The
router's dependency guards every route on it, so a route added here needs no
check of its own."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from climb.api.context import Root, author_id
from climb.api.generation_figures import GenerationFigures, generation_figures
from climb.api.product_figures import ProductFigures, product_figures
from climb.api.workflow_figures import WorkflowFigures, workflow_figures
from climb.cards import CardStore
from climb.drafts import DraftStore
from climb.matches import MatchLog
from climb.outcomes import OutcomeLog
from climb.solution_claims import load_problems
from climb.solutions import SolutionLog

router = APIRouter(prefix="/author", dependencies=[Depends(author_id)])

# the author pages the engine serves, each the last segment of its path
PAGES: list[str] = ["product", "generation", "workflow"]


class AuthorArea(BaseModel):
    pages: list[str]


@router.get("")
def area() -> AuthorArea:
    return AuthorArea(pages=PAGES)


@router.get("/product")
def product(request: Request, root: Root) -> ProductFigures:
    return product_figures(root, now=datetime.now(UTC), dev_user=request.app.state.dev_user)


@router.get("/generation")
def generation(root: Root) -> GenerationFigures:
    return generation_figures(
        OutcomeLog(root).outcomes(),
        DraftStore(root).all(),
        load_problems(root),
        SolutionLog(root).solutions(),
        MatchLog(root).matches(),
        CardStore(root).all(),
        now=datetime.now(UTC),
    )


@router.get("/workflow")
def workflow(root: Root, user_id: Annotated[str, Depends(author_id)]) -> WorkflowFigures:
    return workflow_figures(root, user_id, now=datetime.now(UTC))
