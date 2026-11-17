from climb.schema import Trial
from climb.storage import Database, Log
from climb.trials.table import trials


class TrialLog(Log[Trial]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, trials, Trial)

    def for_problem(self, problem_id: str) -> list[Trial]:
        return self.where(trials.c.problem_id == problem_id)
