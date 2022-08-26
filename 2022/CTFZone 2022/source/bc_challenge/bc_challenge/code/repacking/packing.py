from typing import Sequence, Mapping, Tuple
from types import CodeType
from functools import partial


from iter2 import iter2

from bc_challenge.misc.result_ex import ResultME, collect_all_results
from bc_challenge.misc import with_packed_args
from bc_challenge.code.model import Code, OpCode, SupportedConstTypes
from bc_challenge.code.serialization import mserialize
from .mappings import MODEL_TO_NATIVE_MAPPING, CONSTANTS_USAGE_MAPPING
from .forbidden_opcodes import validate_permitted_opcodes


def pack_code(code: CodeType) -> ResultME[Code]:
    return (
        pack_opcodes_and_constants(code)
        .map(with_packed_args(lambda opcodes, constants: (
            Code(
                opcodes=opcodes,
                constants=constants,
                **{
                    model_attr: getattr(code, native_attr)
                    for model_attr, native_attr in MODEL_TO_NATIVE_MAPPING.items()
                }
            )
        )))
    )


def pack_opcodes_and_constants(code: CodeType) -> ResultME[
    Tuple[Sequence[OpCode], Sequence[SupportedConstTypes]],
]:
    packed_constants = _pack_constants(code) 

    arg_offsets = _generate_arg_offsets(code)

    patched_opcodes = _patch_opcodes(code, arg_offsets)

    validated_opcodes = validate_permitted_opcodes(patched_opcodes)

    return (
        collect_all_results((
            validated_opcodes.alt(lambda err: (err,)),
            packed_constants,
        ))
        .alt(tuple)
    )

# ---

CONSTANTS_ORDER = tuple([
    'co_consts',
    'co_names',
    'co_varnames',
])


def _generate_arg_offsets(code: CodeType) -> Mapping[int, int]:
    sizes = (
        iter2(CONSTANTS_ORDER[:-1])
        .map(lambda attr: len(getattr(code, attr)))
        .to_tuple()
    )

    offsets = (
        iter2.chain((0,), sizes)
        .accumulate()
        .to_tuple()
    )

    return (
        iter2.zip(
            CONSTANTS_ORDER, 
            offsets,
        )
        .map_t(lambda attr, offset: (
            iter2(CONSTANTS_USAGE_MAPPING[attr])
            .map(lambda opcode: (
                opcode, offset
            ))
        ))
        .flatten()
        .to_dict()
    )


def _pack_constants(code: CodeType) -> ResultME[Sequence[SupportedConstTypes]]:
    return (
        iter2(CONSTANTS_ORDER)
        .map(lambda attr: getattr(code, attr))
        .flatten()
        .map(mserialize)
        .apply(collect_all_results)
        .map(tuple)
    )


def _patch_opcode(arg_offsets: Mapping[int, int], opcode: OpCode) -> OpCode:
    offset = arg_offsets.get(opcode[0])
    if offset is None:
        return opcode
    else:
        return opcode[0], opcode[1] + offset


def _patch_opcodes(code: CodeType, arg_offsets: Mapping[int, int]) -> Sequence[OpCode]:
    return (
        iter2(code.co_code)
        .map(int)
        .chunks(2)
        .map(partial(_patch_opcode, arg_offsets))
        .to_tuple()
    )
