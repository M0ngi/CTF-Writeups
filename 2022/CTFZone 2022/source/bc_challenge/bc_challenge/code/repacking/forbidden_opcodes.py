from dataclasses import dataclass

from typing import Sequence

from returns.result import Result, Success, Failure

from iter2 import iter2

from bc_challenge.code.model import OpCode
from bc_challenge.code.opcodes import OPCODE_MAPPING


_FORBIDDEN_OPCODES_STR = (
    'STORE_GLOBAL', 'LOAD_GLOBAL',
    'LOAD_CLOSURE', 
    'STORE_DEREF', 'LOAD_DEREF', 'DELETE_DEREF',
)

_FORBIDDEN_OPCODES = (
    iter2(_FORBIDDEN_OPCODES_STR)
    .map(OPCODE_MAPPING.get)
    .apply(frozenset)
)

_VALID_OPCODES = frozenset(OPCODE_MAPPING.values()) - _FORBIDDEN_OPCODES


@dataclass
class ForbiddenOpcodesError(Exception):
    positions: Sequence[int]


def validate_permitted_opcodes(opcodes: Sequence[OpCode]) -> Result[Sequence[OpCode], ForbiddenOpcodesError]:
    forbidden_opcodes_positions = (
        iter2(opcodes)
        .enumerate()
        .filter_t(lambda _, opcode: (
            opcode[0] not in _VALID_OPCODES
        ))
        .map_t(lambda idx, _: idx)
        .to_tuple()
    )

    if len(forbidden_opcodes_positions) == 0:
        return Success(opcodes)
    else:
        return Failure(
            ForbiddenOpcodesError(forbidden_opcodes_positions)
        )

