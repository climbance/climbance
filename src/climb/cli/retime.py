"""Every served problem's canonicals, run at the drill cap on whichever backend
is configured and each run stored, and each case one of them does not pass
within a tenth of the cap. `corpus.md` gives why a tenth."""

from climb import mint
from climb.generation import Corpus
from climb.runner import judge, runner
from climb.schema import CaseOutcome, SolutionRole
from climb.sitting import DRILL_CAP_MS
from climb.storage import Database

# the most a canonical may take on a case, so the case tests the form rather
# than the machine that ran it
BAR_MS = DRILL_CAP_MS // 10


def retime(root: Database) -> None:
    corpus = Corpus.at(root)
    print(f"runner {runner()}, cap {DRILL_CAP_MS} ms, bar {BAR_MS} ms")
    ran = listed = 0
    for problem in corpus.problems.all():
        if not problem.served:
            continue
        cases = corpus.cases.for_problem(problem.id)
        for canonical in corpus.solutions.for_problem(problem.id, SolutionRole.CANONICAL):
            results = [one for one, _ in judge(canonical.code, cases, cap_ms=DRILL_CAP_MS)]
            # stored, since a run is a fact about the runner: `corpus.md`
            corpus.verifications.append(
                mint.verification(
                    canonical.id, cap_ms=DRILL_CAP_MS, runner=runner(), results=results
                )
            )
            for result in results:
                ran += 1
                if result.outcome is CaseOutcome.PASSED and (result.elapsed_ms or 0) <= BAR_MS:
                    continue
                listed += 1
                taken = f"{result.elapsed_ms} ms" if result.elapsed_ms is not None else "no time"
                print(f"{problem.id}  {canonical.id}  {result.case_id}  {result.outcome}  {taken}")
    print(f"{listed} of {ran} case(s) not passed within {BAR_MS} ms")
