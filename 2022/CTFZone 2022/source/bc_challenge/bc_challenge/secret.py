from typing import Mapping, Optional, Tuple
from pydantic import BaseModel

from returns.maybe import Maybe
from returns.result import safe, Result
from returns.converters import result_to_maybe

from base64 import b64encode, b64decode
import json
import re


class TaskInfo(BaseModel):
    name: str
    access_code: str



class Secret(BaseModel):
    team_id: int
    task_name: str
    flag: Optional[str] 
    next_task: Optional[TaskInfo]

    def pack(self) -> str:
            encoded_secret = b64encode(self.json().encode()).decode()
            return f'SECRET{{{encoded_secret}}}'

    @staticmethod
    def unpack(secret: str) -> Result['Secret', Exception]:
        return (
            safe(lambda: secret[len('SECRET{'):-1])()
            .bind(safe(b64decode))
            .bind(safe(bytes.decode))
            .bind(safe(json.loads))
            .bind(safe(Secret.parse_obj))
        )

    

class SecretsFuncs:
    def __init__(self, tasks_order: Tuple[str], task_access_codes: Mapping[str, str], flags: Mapping[str, str]):
        self._tasks_order = tasks_order
        self._task_access_codes = task_access_codes
        self._flags = flags


    def is_valid_task_access_code(self, task_name: str, access_code: str) -> bool:
        return (
                task_name in self._task_access_codes
            and access_code == self._task_access_codes[task_name]
        )


    def generate_secret_for_task(self, task_name: str, team_id: int) -> str:
        next_task = self._next_task_info(task_name).value_or(None)
        return Secret(
            team_id=team_id,
            task_name=task_name,
            next_task=next_task,
            flag=self._flags.get(task_name),
        ).pack()


    def _next_task_info(self, task_name: str) -> Maybe[TaskInfo]:
        return result_to_maybe(
            safe(self._tasks_order.index)(task_name)
            .bind(lambda idx: (
                safe(lambda: (
                    self._tasks_order[idx + 1]
                ))()
            ))
            .map(lambda next_task_name: (
                TaskInfo(
                    name=next_task_name, 
                    access_code=self._task_access_codes[next_task_name],
                )
            ))
        )

    
_SECRET_RX = re.compile(r'SECRET{[^}]+}')

def search_secret_in_text(text: str) -> Maybe[str]:
    return (
        Maybe.from_optional(
            _SECRET_RX.search(text)
        )
        .map(lambda match: (
            match.group(0)
        ))
    )

