"""The cards and the problems the content browser lists:
`web-app/pages/author/cards/` and `web-app/pages/author/problems/`."""

import json
from collections import Counter
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from climb.cards import CardStore
from climb.cards.graph import depths
from climb.cases import CaseLog
from climb.judgements import ItemStore
from climb.keylines import KeyLineStore
from climb.ladder import ladder
from climb.log import RetirementRequestLog
from climb.matches import MatchLog, standing_matches
from climb.problems import ProblemStore
from climb.ratings import RatingLog, standing_ratings
from climb.schema import (
    Card,
    CaseOutcome,
    ProblemDifficulty,
    RatingSource,
    RetirementReason,
    SolutionRole,
    TestCase,
)
from climb.solution_claims import load_problem, load_problems
from climb.solution_claims.standing import standing_solution_claims
from climb.solution_claims.store import SolutionClaimLog
from climb.solutions import SolutionLog
from climb.statement import signed
from climb.storage import Database
from climb.verifications import VerificationLog


class TemplateCounts(BaseModel):
    template_id: str
    cases: int
    judgement_items: int  # served alone
    keyline_items: int


class RequiredBy(BaseModel):
    card: str  # the requiring card's slug
    template: str  # this card's template it requires
    used_by: str  # the requiring card's template using the form


class AuthorRung(BaseModel):
    problem_id: str
    title: str
    templates: list[str]  # slugs
    difficulty: ProblemDifficulty | None
    score: float | None
    required: bool


class AuthorCard(BaseModel):
    card: Card
    depth: int
    counts: list[TemplateCounts]
    required_by: list[RequiredBy]
    rungs: list[AuthorRung]
    gaps: list[str]  # the core templates no served canonical displays, by slug


class AuthorCards(BaseModel):
    cards: list[AuthorCard]


def author_cards(root: Database) -> AuthorCards:
    cards = CardStore(root).all()
    problems = load_problems(root)
    solutions = SolutionLog(root).solutions()
    matches = MatchLog(root).matches()
    scores = {id: one.score for id, one in standing_ratings(RatingLog(root).ratings()).items()}
    judged = Counter(one.template_id for one in ItemStore(root).served())
    filled = Counter(one.template_id for one in KeyLineStore(root).served())
    deep = depths(cards)
    found: list[AuthorCard] = []
    for card in cards:
        slugs = {one.id: one.slug for one in card.templates}
        # no attempts and no run: the ladder as the corpus derives it now
        resolved = ladder(card, problems, solutions, matches, [])
        found.append(
            AuthorCard(
                card=card,
                depth=deep[card.slug],
                counts=[
                    TemplateCounts(
                        template_id=one.id,
                        cases=len(one.cases),
                        judgement_items=judged[one.id],
                        keyline_items=filled[one.id],
                    )
                    for one in card.templates
                ],
                required_by=[
                    RequiredBy(card=other.slug, template=edge.template, used_by=edge.used_by)
                    for other in cards
                    for edge in other.requires
                    if edge.card == card.slug
                ],
                rungs=[
                    AuthorRung(
                        problem_id=rung.problem.id,
                        title=rung.problem.title,
                        templates=[slugs[one] for one in rung.templates],
                        difficulty=rung.problem.difficulty,
                        score=scores.get(rung.problem.id),
                        required=rung.required,
                    )
                    for rung in resolved.rungs
                ],
                gaps=[gap.slug for gap in resolved.gaps],
            )
        )
    # the card graph's order: a card reads after every card it requires
    found.sort(key=lambda one: (one.depth, one.card.title))
    return AuthorCards(cards=found)


class AuthorProblemRow(BaseModel):
    problem_id: str
    title: str
    target_template: str | None  # the template's slug
    target_technique: str | None
    difficulty: ProblemDifficulty | None  # the standing band, or the generator's label
    score: float | None
    techniques: list[str]
    cases: int
    roles: list[SolutionRole]
    retired_reason: RetirementReason | None  # absent on a served problem
    requests: int
    landed_at: datetime | None  # its first solution's, since a problem stores no time


class AuthorProblems(BaseModel):
    problems: list[AuthorProblemRow]


def _template_slugs(root: Database) -> dict[str, str]:
    return {one.id: one.slug for card in CardStore(root).all() for one in card.templates}


def author_problems(root: Database) -> AuthorProblems:
    slugs = _template_slugs(root)
    scores = {id: one.score for id, one in standing_ratings(RatingLog(root).ratings()).items()}
    cases = Counter(one.problem_id for one in CaseLog(root).cases())
    requests = Counter(one.problem_id for one in RetirementRequestLog(root).all())
    roles: dict[str, set[SolutionRole]] = {}
    landed: dict[str, datetime] = {}
    for one in SolutionLog(root).solutions():
        roles.setdefault(one.problem_id, set()).add(one.role)
        landed[one.problem_id] = min(landed.get(one.problem_id, one.created_at), one.created_at)
    rows = [
        AuthorProblemRow(
            problem_id=problem.id,
            title=problem.title,
            target_template=slugs.get(problem.target_template_id or ""),
            target_technique=problem.target_technique,
            difficulty=problem.difficulty,
            score=scores.get(problem.id),
            techniques=problem.techniques,
            cases=cases[problem.id],
            roles=[role for role in SolutionRole if role in roles.get(problem.id, set())],
            retired_reason=problem.retired_reason,
            requests=requests[problem.id],
            landed_at=landed.get(problem.id),
        )
        for problem in load_problems(root)
    ]
    # newest first: the author reads what the last run landed first
    rows.sort(key=lambda one: (one.landed_at is not None, one.landed_at, one.problem_id))
    return AuthorProblems(problems=rows[::-1])


class AuthorSolution(BaseModel):
    role: SolutionRole
    code: str
    outcome: CaseOutcome | None  # its latest verification's; absent where none ran
    displays: list[str]  # template slugs, from the standing matches
    claims: list[str]  # from the standing solution claim


class AuthorCase(BaseModel):
    id: str
    args: str  # the arguments as one line, cut
    expected: str  # the expected return as one line, cut
    size: int  # bytes of the arguments and the expected return whole, as JSON
    round: int | None
    repeats: int


class AuthorCaseWhole(BaseModel):
    args: list[Any]
    expected: Any


# a case may weigh up to the ceiling, so an opened problem carries each cut
LINE = 120


def _line(value: object) -> tuple[str, int]:
    text = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    size = len(text.encode())
    return (text if len(text) <= LINE else f"{text[: LINE - 1]}…"), size


def _author_case(one: TestCase) -> AuthorCase:
    args, args_size = _line(one.args)
    expected, expected_size = _line(one.expected)
    return AuthorCase(
        id=one.id,
        args=args,
        expected=expected,
        size=args_size + expected_size,
        round=one.round,
        repeats=one.repeats,
    )


def author_case(root: Database, problem_id: str, case_id: str) -> AuthorCaseWhole | None:
    found = [one for one in CaseLog(root).for_problem(problem_id) if one.id == case_id]
    return AuthorCaseWhole(args=found[0].args, expected=found[0].expected) if found else None


class AuthorRating(BaseModel):
    created_at: datetime
    score: float
    deviation: float | None
    source: RatingSource
    standing: bool


class AuthorProblem(BaseModel):
    problem_id: str
    statement: str  # the prose, as the sitting serves it
    signature: str | None
    generator: ProblemDifficulty | None  # the label the generator wrote
    solutions: list[AuthorSolution]
    cases: list[AuthorCase]
    ratings: list[AuthorRating]  # latest first


def _latest_outcome(verifications: VerificationLog, solution_id: str) -> CaseOutcome | None:
    runs = verifications.for_solution(solution_id)
    return max(runs, key=lambda run: run.created_at).outcome if runs else None


def author_problem(root: Database, problem_id: str) -> AuthorProblem | None:
    problem = load_problem(root, problem_id)
    stored = ProblemStore(root).get(problem_id)
    if problem is None or stored is None:
        return None
    slugs = _template_slugs(root)
    solutions = SolutionLog(root).for_problem(problem_id)
    ids = {one.id for one in solutions}
    claims = standing_solution_claims(
        one for one in SolutionClaimLog(root).claims() if one.solution_id in ids
    )
    displays: dict[str, list[str]] = {}
    for (template_id, solution_id), match in standing_matches(MatchLog(root).matches()).items():
        if match.matched and solution_id in ids and template_id in slugs:
            displays.setdefault(solution_id, []).append(slugs[template_id])
    verifications = VerificationLog(root)
    ratings = sorted(RatingLog(root).for_problem(problem_id), key=lambda one: one.created_at)
    stands = standing_ratings(ratings).get(problem_id)
    prose, signature = signed(problem.statement)
    order = list(SolutionRole)
    return AuthorProblem(
        problem_id=problem.id,
        statement=prose,
        signature=signature,
        generator=stored.difficulty,
        solutions=[
            AuthorSolution(
                role=one.role,
                code=one.code,
                outcome=_latest_outcome(verifications, one.id),
                displays=sorted(displays.get(one.id, [])),
                claims=claims[one.id].techniques if one.id in claims else [],
            )
            for one in sorted(solutions, key=lambda one: order.index(one.role))
        ],
        cases=[_author_case(one) for one in CaseLog(root).for_problem(problem_id)],
        ratings=[
            AuthorRating(
                created_at=one.created_at,
                score=one.score,
                deviation=one.deviation,
                source=one.source,
                standing=stands is not None and one.id == stands.id,
            )
            for one in reversed(ratings)
        ],
    )
