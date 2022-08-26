from typing import Sequence, Any

from iter2 import iter2

from bc_challenge.code.serialization import mserialize, mdeserialize
from bc_challenge.misc.result_ex import ResultME, collect_all_results


@mserialize.instance(tuple)
def _mserialize_tuple(native: tuple) -> ResultME[tuple]:
    return _mserialize_sequence(native)


@mdeserialize.instance(tuple)
def _mdeserialize_tuple(model: tuple) -> ResultME[tuple]:
    return _mdeserialize_sequence(model)


@mdeserialize.instance(list)
def _mdeserialize_list(model: list) -> ResultME[tuple]:
    return _mdeserialize_sequence(model)


# ---


def _mserialize_sequence(seq: Sequence[Any]) -> ResultME[tuple]:
    return (
        iter2(seq)
        .map(mserialize)
        .apply(collect_all_results)
        .map(tuple)
    )

def _mdeserialize_sequence(seq: Sequence[Any]) -> ResultME[tuple]:
    return (
        iter2(seq)
        .map(mdeserialize)
        .apply(collect_all_results)
        .map(tuple)
    )
