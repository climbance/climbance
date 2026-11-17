from climb.log.table import retirement_requests
from climb.schema import RetirementRequest
from climb.storage import Database, Log


class RetirementRequestLog(Log[RetirementRequest]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, retirement_requests, RetirementRequest)

    def for_user(self, user_id: str) -> list[RetirementRequest]:
        return self.where(retirement_requests.c.user_id == user_id)

    def for_problem(self, problem_id: str) -> list[RetirementRequest]:
        return self.where(retirement_requests.c.problem_id == problem_id)
