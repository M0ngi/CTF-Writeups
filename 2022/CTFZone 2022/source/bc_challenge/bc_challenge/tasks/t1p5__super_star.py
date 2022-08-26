# [TaskConfig]
# hide_secret_in_vault_with_name=SECRET_IN_VAULT

from typing import Sequence

from iter2 import iter2
from returns.result import safe, Success, Failure
from bc_challenge.misc.result_ex import ResultME, collect_all_results

from bc_challenge.code import opcodes as opc
from bc_challenge.code.serialization import mdeserialize
from bc_challenge.code.model import CodePatch
from bc_challenge.code.patching import apply_patch_to


def run(patch: CodePatch) -> ResultME[str]:

    # Sanbox to patch
    def sandbox():
        ...

    # Restrictions definitions
    only_vault = _restrict_import_to_namespace(
        'bc_challenge.namespaces.vault',
        patch
    )

    only_six_opcodes = _limit_opcodes_count(6, patch)
    only_ten_constants = _limit_constants_count(10, patch)

    forbid_extraction_from_module = _forbid_opcodes([
        opc.IMPORT_FROM,
        opc.LOAD_ATTR,
    ], patch)

    no_inner_functions = _forbid_opcodes([
        opc.MAKE_FUNCTION,
    ], patch)

    # The Show
    return (
        collect_all_results([  # apply restrictions
            only_vault,
            only_six_opcodes,
            only_ten_constants,
            forbid_extraction_from_module,
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
