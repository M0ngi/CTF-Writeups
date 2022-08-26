from typing import Sequence

from bc_challenge.misc.result_ex import ResultME, collect_all_results
from bc_challenge.misc import with_packed_args

from bc_challenge.code.compilation import compile_single_function
from bc_challenge.code.patching import create_patch

from bc_challenge.code.model import CodePatch, SupportedNativeTypes
from bc_challenge.code.assembling import assemble_source

from bc_challenge.code.model import CodePatch
from bc_challenge.code.serialization import mserialize


def create_patch_from_source(source: str) -> ResultME[CodePatch]:
    return (
        compile_single_function(source)
        .alt(lambda err: (err,))
        .bind(create_patch)
    )


def create_patch_from_opcodes_and_constants(
    source: str, 
    constants: Sequence[SupportedNativeTypes]
) -> ResultME[CodePatch]:
    return (
        collect_all_results((
            assemble_source(source),
            mserialize(tuple(constants)),
        ))
        .map(with_packed_args(lambda opcodes, constants: (
            CodePatch(
                opcodes=opcodes,
                constants=constants,
            )
        )))
    )
