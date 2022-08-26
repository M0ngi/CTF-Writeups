from returns.result import ResultE

from types import CodeType

from bc_challenge.code.serialization import mserialize, mdeserialize
from bc_challenge.code.model import Code

from bc_challenge.code.repacking.packing import pack_code
from bc_challenge.code.repacking.unpacking import unpack_code


@mserialize.instance(CodeType)
def _mserialize_CodeType(native: CodeType) -> ResultE[Code]:
    return pack_code(native)


@mdeserialize.instance(Code)
def _mdeserialize_Code(model: Code) -> ResultE[CodeType]:
    return unpack_code(model)