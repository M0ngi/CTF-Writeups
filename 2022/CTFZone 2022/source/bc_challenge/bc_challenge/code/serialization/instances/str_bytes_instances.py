from curses.ascii import isascii
from statistics import mode
from typing import Union

from base64 import b64encode, b64decode

from returns.result import Success, Failure, safe

from bc_challenge.misc.result_ex import ResultME
from bc_challenge.code.serialization import mserialize, mdeserialize
from bc_challenge.code.model import StrOrBytes


@mserialize.instance(str)
def _mserialize_str(native: str) -> ResultME[StrOrBytes]:
    return Success(
        StrOrBytes(
            is_bytes=False,
            value=native,
        )
    )


@mserialize.instance(bytes)
def _mserialize_bytes(native: bytes) -> ResultME[StrOrBytes]:
    return Success(
        StrOrBytes(
            is_bytes=True,
            value=b64encode(native),
        )
    )


@mdeserialize.instance(StrOrBytes)
def _mdeserialize_StrOrBytes(model: StrOrBytes) -> ResultME[Union[str, bytes]]:
    if model.is_bytes:
        return safe(b64decode)(model.value)
    else:
        s = model.value
        if s.isascii():
            return Success(s)
        else:
            return Failure((Exception(
                'Only ascii allowed'
            ),))
