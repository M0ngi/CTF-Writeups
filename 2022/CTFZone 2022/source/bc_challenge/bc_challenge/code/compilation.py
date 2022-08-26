from types import CodeType

from returns.result import safe, Result


def compile_single_function(source: str) -> Result[CodeType, Exception]:
    return (
        safe(compile)(
            source,
            'THE_SANDBOX',
            'single',
        )
        .map(lambda module_code: (
            module_code.co_consts[0]  # must be code object 
        ))
        .bind(lambda possible_code_for_patch: (
            _assert_CodeType(possible_code_for_patch)
        ))
    )


@safe
def _assert_CodeType(obj):
    if not isinstance(obj, CodeType):
        raise Exception('Not a CodeType provided as patch')
    return obj