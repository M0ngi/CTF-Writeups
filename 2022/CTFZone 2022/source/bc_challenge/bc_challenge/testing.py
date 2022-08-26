from typing import Tuple, TypeVar, Callable

from multiprocessing import Pool
from returns.result import safe

from returns.converters import flatten
from bc_challenge.misc.result_ex import ResultME, resolve_failure
from bc_challenge.misc import with_packed_args

from bc_challenge.code.model import CodePatch
from bc_challenge.task_running import run_task


def test_solution(task_name: str) -> Tuple[bool, str]:
    secret = _generate_secret()
    text = resolve_failure(
        _read_task_source_and_solution(task_name)
        .bind(with_packed_args(lambda source, solution: (
            run_task_isolated(
                task_source=source,
                patch=solution,
                secret=secret,
            )
        ))),
        repr
    )
    secret_idx = text.find(secret)
    return secret_idx != -1, _highlight_secret(text, secret_idx)


def run_task_isolated(task_source: str, patch: CodePatch, secret: str) -> ResultME[str]:
    return flatten(
        _run_isolated(
            _run_task, (
                task_source,
                patch,
                secret,
            )
        )
    )


# ---


def _run_task(task_source: str, patch: CodePatch, secret: str) -> ResultME[str]:
    return run_task(
        task_source=task_source,
        patch=patch,
        secret=secret,
    )


_R = TypeVar('_R')

def _run_isolated(fn: Callable[..., _R], args) -> ResultME[_R]:
    return (
        safe(Pool(1).apply)(fn, args)
        .alt(lambda err: (err,))
    )



@safe
def _read_task_source_and_solution(name: str) -> Tuple[str, CodePatch]:
    with open(f'./bc_challenge/tasks/{name}.py') as task_file:
        source = task_file.read()

    from importlib import import_module
    solution = import_module('bc_challenge.solutions.' + name).SOLUTION

    return source, solution


# ---

SECRET_DATA_SIZE = 10
SECRET_SIZE = len('SECRET{}') + SECRET_DATA_SIZE


def _highlight_secret(text: str, pos: int) -> str:
    return (
        f'{text[:pos]}\033[1m{text[pos: pos + SECRET_SIZE]}\033[0m{text[pos + SECRET_SIZE:]}'
        if pos != -1 else text
    )


def _generate_secret() -> str:
    import random
    import string

    chrs = string.ascii_uppercase + string.digits + '_'
    random_chrs = random.choices(chrs, k=SECRET_DATA_SIZE)

    return ''.join(['SECRET{', *random_chrs, '}'])
