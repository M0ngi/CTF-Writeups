import httpx

from returns.result import Result, Success, Failure, safe

from bc_challenge.api.models import ReqTaskSource, ReqSubmitSolution, TaskInfo
from bc_challenge.code.model import CodePatch


class ApiClient:
    def __init__(self, *, api_url: str, team_token: str):
        self.api_url = api_url
        self.team_token = team_token

    def _ask(self, path, **options) -> Result[str, Exception]:
        return (
            safe(httpx.post)(
                f'{self.api_url}{path}',
                headers={
                    'X-Token': self.team_token,
                },
                timeout=20,
                **options
            )
            .bind(lambda resp: (
                Success(resp.text) if resp.status_code == 200
                else Failure(Exception(resp.text))
            ))
        )


    def download_task_source(self, task_name: str, access_code: str) -> Result[str, Exception]:
        return (
            self._ask('/task_source', json=(
                ReqTaskSource(
                    task=TaskInfo(
                        name=task_name,
                        access_code=access_code,
                    )
                ).dict()
            ))
        )


    def submit_solution(self, task_name: str, access_code: str, solution: CodePatch) -> Result[str, Exception]:
        return (
            self._ask('/submit_solution', json=(
                ReqSubmitSolution(
                    task=TaskInfo(
                        name=task_name,
                        access_code=access_code,
                    ),
                    solution=solution,
                ).dict()
            ))
        )
