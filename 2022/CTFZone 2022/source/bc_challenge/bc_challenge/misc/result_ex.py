from typing import Callable, Optional, Sequence, Union
from typing import TypeVar

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful


_V = TypeVar('_V')
ResultME = Result[_V, Sequence[Exception]]

_T = TypeVar('_T')
_T2 = TypeVar('_T2')
_Err = TypeVar('_Err')


def collect_all_results(rs: Sequence[Result[_T, Sequence[_Err]]]) -> Result[Sequence[_T], Sequence[_Err]]:
    seq = []
    save = seq.append
    save_many = seq.extend

    rs_it = iter(rs)

    for r in rs_it:
        if is_successful(r):
            save(r.unwrap())
        else:
            seq.clear()                 # 1. drop good ones
            save_many(r.failure())      # 2. save first error
            break                       # 3. jump to error collection loop
    else:
        return Success(seq)

    for r in rs_it:
        if not is_successful(r):
            save_many(r.failure())
    else:
        return Failure(seq)
    

def assert_not_none(obj: Optional[_T], failure_callback: Callable[[], _Err]) -> Result[_T, _Err]:
    if obj is None:
        return Failure(failure_callback())
    else:
        return Success(obj)


def resolve_failure(r: Result[_T, _Err], resolve_fn: Callable[[_Err], _T2]) -> Union[_T, _T2]:
    if is_successful(r):
        return r.unwrap()
    else:
        return resolve_fn(r.failure())
