"""The routes the author pages read: `web-app/pages/author/README.md`. The
router's dependency guards every route on it, so a route added here needs no
check of its own."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from climb.api.author_content import (
    AuthorCards,
    AuthorCaseWhole,
    AuthorProblem,
    AuthorProblems,
    author_cards,
    author_case,
    author_problem,
    author_problems,
)
from climb.api.context import Root, author_id
from climb.api.generation_figures import GenerationFigures, generation_figures
from climb.api.inbox_figures import InboxFigures, inbox_figures
from climb.api.product_figures import ProductFigures, product_figures
from climb.api.spend_figures import SpendFigures, spend_figures
from climb.cards import CardStore
from climb.drafts import DraftStore
from climb.knowledge.seed import seeded_concepts
from climb.matches import MatchLog
from climb.outcomes import OutcomeLog
from climb.schema import Concept
from climb.solution_claims import load_problems
from climb.solutions import SolutionLog

router = APIRouter(prefix="/author", dependencies=[Depends(author_id)])

# the author pages the engine serves, each the last segment of its path
PAGES: list[str] = [
    "product",
    "generation",
    "spend",
    "questions",
    "lessons",
    "cards",
    "problems",
]


class AuthorArea(BaseModel):
    pages: list[str]


class AuthorConcepts(BaseModel):
    concepts: list[Concept]


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


@router.get("/spend")
def spend(root: Root) -> SpendFigures:
    return spend_figures(root, now=datetime.now(UTC))


@router.get("/inbox")
def inbox(root: Root, user_id: Annotated[str, Depends(author_id)]) -> InboxFigures:
    return inbox_figures(root, user_id, now=datetime.now(UTC))


@router.get("/concepts")
def concepts(root: Root, module: str) -> AuthorConcepts:
    return AuthorConcepts(concepts=seeded_concepts(module, root=root))


@router.get("/cards")
def cards(root: Root) -> AuthorCards:
    return author_cards(root)


@router.get("/problems")
def problems(root: Root) -> AuthorProblems:
    return author_problems(root)


@router.get("/problems/{problem_id}")
def problem(root: Root, problem_id: str) -> AuthorProblem:
    found = author_problem(root, problem_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"no problem {problem_id}")
    return found


@router.get("/problems/{problem_id}/cases/{case_id}")
def problem_case(root: Root, problem_id: str, case_id: str) -> AuthorCaseWhole:
    found = author_case(root, problem_id, case_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"no case {case_id} on {problem_id}")
    return found
