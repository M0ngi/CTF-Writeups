# [TaskConfig]
# put_secret_as_kwarg_with_name=secret

from typing import Sequence

from iter2 import iter2
from returns.result import safe, Success, Failure
from bc_challenge.misc.result_ex import ResultME, collect_all_results

from bc_challenge.code import opcodes as opc
from bc_challenge.code.model import CodePatch
from bc_challenge.code.patching import apply_patch_to


def run(patch: CodePatch, *, secret: str) -> ResultME[str]:

    # Sanbox to patch
    def sandbox(secret):
        ...

    # Restrictions definitions
    only_two_opcodes = _limit_opcodes_count(2, patch)
    only_two_constants = _limit_constants_count(2, patch)

    no_inner_functions = _forbid_opcodes([
        opc.MAKE_FUNCTION,
    ], patch)

    # The Show
    return (
        collect_all_results([  # apply restrictions
            only_two_opcodes,
            only_two_constants,
            no_inner_functions,
        ])
        .bind(lambda _: (

            apply_patch_to(sandbox, patch)
            
            .map(safe)  # `safe` is not about sandboxing, 
                        # it captures exceptions into Result

            .bind(lambda safe_patched_sandbox: (
                safe_patched_sandbox(secret)  
            ))

            .map(repr)  # string representation of value
                        # returned from sandbox 
        ))
    )


# ---

def _assert(cond: bool, msg: str) -> ResultME[None]:
    try:
        assert cond, msg
        return Success(None)
    except AssertionError as ex:
        return Failure((ex,))


def _limit_opcodes_count(n: int, patch: CodePatch) -> ResultME[None]:
    return _assert(
        len(patch.opcodes) <= n,
        'Opcodes count limit exceeded'
    )


def _limit_constants_count(n: int, patch: CodePatch) -> ResultME[None]:
    return _assert(
        len(patch.constants) <= n,
        'Constants count limit exceeded'
    )


def _forbid_opcodes(forbidden_opcodes: Sequence[int], patch: CodePatch) -> ResultME[None]:
    return _assert(
        (
            iter2(patch.opcodes)
            .all_t(lambda op, _: (
                op not in forbidden_opcodes
            ))
        ),
        'Forbidden opcode'
    )