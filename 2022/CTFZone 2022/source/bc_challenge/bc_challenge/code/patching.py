from types import CodeType, FunctionType
from typing import Mapping

from returns.result import safe

from bc_challenge.misc import with_packed_args
from bc_challenge.misc.result_ex import ResultME

from .model import CodePatch, SupportedNativeTypes
from .repacking.packing import pack_opcodes_and_constants
from .repacking.unpacking import unpack_opcodes_and_constants



def create_patch(code: CodeType) -> ResultME[CodePatch]:
    return (
        pack_opcodes_and_constants(code)
        .bind(with_packed_args(lambda opcodes, constants: (
            safe(CodePatch)(
                opcodes=opcodes,
                constants=constants,
            )
            .alt(lambda err: (err,))
        )))
    )


def apply_patch_to(f: FunctionType, patch: CodePatch) -> ResultME[FunctionType]:
    return (
        unpack_opcodes_and_constants(
            patch.opcodes,
            patch.constants,
        )
        .map(with_packed_args(lambda opcode_bytes, attrs_with_constants: (
            _apply_patch_to(
                f, 
                opcode_bytes,
                attrs_with_constants,
            )
        )))
    )


def _apply_patch_to(
    f: FunctionType, 
    opcode_bytes: bytes, 
    attrs_with_constants: Mapping[str, SupportedNativeTypes]
) -> FunctionType:
    orig_code = f.__code__
    patched_code = orig_code.replace(
        co_code=opcode_bytes,
        **attrs_with_constants
    )
    f.__code__ = patched_code
    return f