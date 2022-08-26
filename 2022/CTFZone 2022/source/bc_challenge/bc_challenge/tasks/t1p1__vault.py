# [TaskConfig]
# hide_secret_in_vault_with_name=SECRET_IN_VAULT
# put_secret_length_as_kwarg_with_name=secret_size

from functools import partial
from typing import Sequence

from iter2 import iter2
from returns.result import safe, Success, Failure
from bc_challenge.misc.result_ex import ResultME, collect_all_results

from bc_challenge.code import opcodes as opc
from bc_challenge.code.serialization import mdeserialize
from bc_challenge.code.model import CodePatch
from bc_challenge.code.patching import apply_patch_to


def run(patch: CodePatch, *, secret_size: int) -> ResultME[str]:

    # Sanbox to patch
    def sandbox():
        ...

    # Restrictions definitions
    only_vault = _restrict_import_to_namespace(
        'bc_challenge.namespaces.vault',
        patch
    )

    only_ten_opcodes = _limit_opcodes_count(10, patch)
    only_ten_constants = _limit_constants_count(10, patch)

    near_secret_size_permitted = partial(
        _limit_result_size,
        secret_size + 2
    )

    no_inner_functions = _forbid_opcodes([
        opc.MAKE_FUNCTION,
    ], patch)

    # The Show
    return (
        collect_all_results([  # apply restrictions
            only_vault,
            only_ten_opcodes,
            only_ten_constants,
            no_inner_functions,
        ])
        .bind(lambda _: (
            apply_patch_to(sandbox, patch)
            
            .map(safe)  # `safe` is not about sandboxing, 
                        # it captures exceptions into Result

            .bind(lambda safe_patched_sandbox: (
                safe_patched_sandbox()  
            ))

            .map(repr)  # string representation of value
                        # returned from sandbox 
        ))
        .bind(lambda result: (  
            collect_all_results([ # apply result restrictions
                near_secret_size_permitted(result),
            ])
            .map(lambda _: (
                result
            )) 
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


def _limit_result_size(n: int, result: str) -> ResultME[None]:
    return _assert(
        len(result) <= n,
        'Result character size exceeded'
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


def _restrict_import_to_namespace(namespace_module: str, patch: CodePatch) -> ResultME[None]:
    constants = patch.constants
    constant_value = safe(lambda idx: (
        constants[idx]
    ))

    UNDEFINED = object()

    return _assert(
        (
            iter2(patch.opcodes)
            .filter_t(lambda op, _: (
                op == opc.IMPORT_NAME 
            ))
            .map_t(lambda _, arg: (
                constant_value(arg)
                .bind(mdeserialize)
                .value_or(UNDEFINED)
            ))
            .all(lambda value: (
                isinstance(value, str)
                and
                value == namespace_module
            ))

        ),
        'Import of forbidden module'
    )
