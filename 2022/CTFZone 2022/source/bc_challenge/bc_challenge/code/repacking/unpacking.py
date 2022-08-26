from typing import Sequence, Mapping, Tuple
from types import CodeType

from returns.result import safe

from iter2 import iter2

from bc_challenge.misc.result_ex import ResultME, collect_all_results
from bc_challenge.misc import with_packed_args
from bc_challenge.code.model import Code, OpCode, SupportedConstTypes, SupportedNativeTypes
from bc_challenge.code.serialization import mdeserialize
from .mappings import NATIVE_TO_MODEL_MAPPING, NATIVE_POHUI_FIELDS_CONSTANTS, CONSTANTS_USAGE_MAPPING
from .forbidden_opcodes import validate_permitted_opcodes


def unpack_code(code: Code) -> ResultME[CodeType]:
    return (
        unpack_opcodes_and_constants(
            code.opcodes,
            code.constants,
        )
        .bind(with_packed_args(lambda opcode_bytes, attrs_with_constants: (
            _build_CodeType(
                co_code=opcode_bytes,
                **attrs_with_constants,
                **{
                    native_attr: getattr(code, model_attr)
                    for native_attr, model_attr in NATIVE_TO_MODEL_MAPPING.items()
                },
                **NATIVE_POHUI_FIELDS_CONSTANTS
            )
            .alt(lambda err: (' '.join((
                f'Failed to build CodeType: {err}.',
                '(TODO: Strange issue, requires research.', 
                'Everything fine if inner function is defined with args,',
                'uses constants and loads attributes of objects.',
                'May be it is related to intimidating code about manual building of CodeType.)'
            )),))
        )))
    )


def unpack_opcodes_and_constants(
    opcodes: Sequence[OpCode],
    constants: Sequence[SupportedConstTypes],
) -> ResultME[
    Tuple[bytes, Mapping[str, Sequence[SupportedNativeTypes]]],
]:
    validated_opcodes = validate_permitted_opcodes(opcodes)
    deserialized_constants = _deserialize_constants(constants)

    return (
        collect_all_results((
            validated_opcodes.alt(lambda err: (err,)),
            deserialized_constants,
        ))
        .map(
            with_packed_args(_unpack_opcodes_and_constants)
        )
    )


# ---

_CODE_TYPE_POS_ARG_ORDER = (
    'co_argcount', 
    'co_posonlyargcount', 
    'co_kwonlyargcount', 
    'co_nlocals', 
    'co_stacksize',
    'co_flags', 
    'co_code',
    'co_consts', 
    'co_names', 
    'co_varnames', 
    'co_filename', 
    'co_name',
    'co_firstlineno', 
    'co_lnotab',
)


@safe
def _build_CodeType(**native_attrs) -> CodeType:
    return CodeType(*(
        native_attrs[attr]
        for attr in _CODE_TYPE_POS_ARG_ORDER
    ))


def _deserialize_constants(
    constants: Sequence[SupportedConstTypes],
) -> ResultME[Sequence[SupportedNativeTypes]]:
    return (
        iter2(constants)
        .map(mdeserialize)
        .apply(collect_all_results)
    )


def _unpack_opcodes_and_constants(
    opcodes: Sequence[OpCode], 
    constants: Sequence[SupportedNativeTypes],
) -> Tuple[
    bytes,
    Mapping[str, Sequence[SupportedNativeTypes]],
]:
    usage_register = {
        attr: {}
        for attr in CONSTANTS_USAGE_MAPPING
    }

    usage_register_by_opcode = (
        iter2(CONSTANTS_USAGE_MAPPING.items())
        .map_t(lambda attr, opcodes: (
            usage_register[attr], opcodes
        ))
        .map_t(lambda usage_reg, opcodes:(
            iter2(opcodes)
            .map(lambda opcode: (opcode, usage_reg))
        ))
        .flatten()
        .to_dict()
    )

    def _patch_opcode(opcode: OpCode) -> OpCode:
        op, arg = opcode
        if op not in usage_register_by_opcode:
            return opcode

        reg = usage_register_by_opcode[op]
        if arg in reg:
            return op, reg[arg]
        else:
            new_arg = reg[arg] = len(reg)  # RENUMERATE CONSTANTS by ACCESS ORDER
            return op, new_arg

    packed_opcodes = (
        iter2(opcodes)
        .map(_patch_opcode)
        .flatten()
        .map(lambda d: (
            (d & 0xff).to_bytes(1, 'little')
        ))
        .join(b'')
    )

    constants_attrs = (
        iter2(usage_register.items())
        .map_t(lambda attr, reg: (
            attr,
            iter2(reg.items())
                .map_t(lambda idx, new_idx: (
                    new_idx, 
                    safe(lambda: constants[idx])()
                ))
                .sort(key=lambda t: t[0])
                .map_t(lambda _, v: (
                    v.alt(lambda err: (err,))
                ))
                .apply(collect_all_results)
                .map(tuple)
                .value_or(())
        ))
        .filter_t(lambda _, overrides: (
            len(overrides) > 0  # DO NOT OVERRIDE if no constants provided
        ))
        .to_dict()
    )

    return packed_opcodes, constants_attrs

