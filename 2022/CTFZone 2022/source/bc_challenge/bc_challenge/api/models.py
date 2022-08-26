from pydantic import BaseModel

from bc_challenge.code.model import CodePatch
from bc_challenge.secret import TaskInfo


class ReqTaskSource(BaseModel):
    task: TaskInfo


class ReqSubmitSolution(BaseModel):
    task: TaskInfo
    solution: CodePatch