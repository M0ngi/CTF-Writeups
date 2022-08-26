from typing import TypeVar

from classes import typeclass, AssociatedType

from bc_challenge.misc.result_ex import ResultME


_Native = TypeVar('_Native')
_Model = TypeVar('_Model')


class MSerializable(AssociatedType):
    '''MSerializable type can be `mserialize`d'''


class MDeserializable(AssociatedType):
    '''MDeserializable type can be `mdeserialize`d'''



@typeclass(MSerializable)
def mserialize(native: _Native) -> ResultME[_Model]:
    ...


@typeclass(MDeserializable)
def mdeserialize(model: _Model) -> ResultME[_Native]:
    ...

