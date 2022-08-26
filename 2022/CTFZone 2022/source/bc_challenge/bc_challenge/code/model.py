from typing import Union, Tuple, Sequence, TypeVar
from types import CodeType

from pydantic import BaseModel


# ---

_T = TypeVar('_T')

_Tupled = Union[_T, Tuple[_T, ...]]

_TupledN = _Tupled[_Tupled[_Tupled]] 

# ---


OpCode = Tuple[int, int]

_SupportedPrimitiveConstTypes = Union[
    None,
    bool,
    int, float, 
    'StrOrBytes',
    'Code',
]

SupportedConstTypes = _TupledN[_SupportedPrimitiveConstTypes]

_SupportedPrimitiveNativeTypes = Union[
    None,
    bool,
    int, float, 
    str, bytes, 
    CodeType,
]

SupportedNativeTypes = _TupledN[_SupportedPrimitiveNativeTypes]


class StrOrBytes(BaseModel):
    is_bytes: bool = False
    value: str


class Code(BaseModel):
    name: str
    opcodes: Sequence[OpCode]
    constants: Sequence[SupportedConstTypes]
    flags: int
    arg_count: int
    pos_only_arg_count: int
    kw_only_arg_count: int
    locals_count: int


class CodePatch(BaseModel):
    opcodes: Sequence[OpCode]
    constants: Sequence[SupportedConstTypes]
