from returns.result import Success

from bc_challenge.misc.result_ex import ResultME
from bc_challenge.code.serialization import mserialize, mdeserialize


@mserialize.instance(None)
def _mserialize_None(native: None) -> ResultME[None]:
    return Success(None)


@mdeserialize.instance(None)
def _mdeserialize_None(model: None) -> ResultME[None]:
    return Success(None)


@mserialize.instance(bool)
def _mserialize_bool(native: bool) -> ResultME[bool]:
    return Success(native)


@mdeserialize.instance(bool)
def _mdeserialize_bool(model: bool) -> ResultME[bool]:
    return Success(model)


@mserialize.instance(int)
def _mserialize_int(native: int) -> ResultME[int]:
    return Success(native)


@mdeserialize.instance(int)
def _mdeserialize_int(model: int) -> ResultME[int]:
    return Success(model)


@mserialize.instance(float)
def _mserialize_float(native: float) -> ResultME[float]:
    return Success(native)


@mdeserialize.instance(float)
def _mdeserialize_float(model: float) -> ResultME[float]:
    return Success(model)





