from typing import Sequence

from opcode import opmap as OPCODE_MAPPING

from iter2 import iter2

from bc_challenge.misc.result_ex import ResultME, collect_all_results
from bc_challenge.misc import with_packed_args

from bc_challenge.code.model import Code, CodePatch, OpCode, SupportedConstTypes, SupportedNativeTypes
from bc_challenge.code.assembling import disassemble_opcodes
from bc_challenge.code.serialization import mdeserialize


REVERSE_OPCODE_MAPPING = {
    code: name
    for name, code in OPCODE_MAPPING.items()
}


def log_opcodes(opcodes):
    print('---')
    for opcode in opcodes:
        code, arg = opcode
        name = REVERSE_OPCODE_MAPPING.get(code, f'<UNK: {code}>')
        print(f'{name!s:20} {arg}')
    print('---')


def pretty_print_code_patch(patch: CodePatch) -> None:
    (
        _pretty_format_code_patch(patch)
        .map(lambda lines: (
            iter2(lines)
            .foreach(print)
        ))
        .alt(lambda errors: (
            iter2.chain(
                ('--- Invalid CodePatch ---',),
                (
                    iter2(errors)
                    .enumerate(count_from=1)
                    .map_t(lambda idx, error: (
                        f'{idx!s:>2}: {error}'
                    ))
                )
            )
            .foreach(print)
        ))
    )


def print_code_patch_as_python_code(patch: CodePatch):
    return (
        collect_all_results((
            (
                disassemble_opcodes(patch.opcodes)
                .map(lambda lines: (
                    '\n'.join(lines)
                ))
            ),
            (
                iter2(patch.constants)
                .map(mdeserialize)
                .apply(collect_all_results)
                .map(lambda constants: (
                    iter2(constants)
                    .map(repr)
                    .enumerate()
                    .map_t(lambda idx, s: f'    {s},  # {idx}')
                    .join('\n')
                ))
            ),
        ))
        .map(with_packed_args(lambda source_lines, constants_lines: (
            _format_solution(source_lines, constants_lines)
        )))
        .map(print)
        .alt(lambda errs: (
            print(f'Failed to dump solution as python code:\n{errs!r}')
        ))
    )

# ---

def _pretty_format_code_patch(patch: CodePatch) -> ResultME[Sequence[str]]:
    return (
        _pretty_format_opcodes_and_constants(
            patch.opcodes,
            patch.constants,
        )
        .map(lambda opcodes_constants_strs: (
            iter2.chain(
                ('--- CodePatch ---',),
                opcodes_constants_strs
            )
            .to_tuple()
        ))
    )


def _pretty_format_opcodes(opcodes: Sequence[OpCode]) -> ResultME[Sequence[str]]:
    return (
        disassemble_opcodes(opcodes)
        .map(lambda opcodes_lines: (
            iter2(opcodes_lines)
            .enumerate()
            .map_t(lambda idx, line: (
                f'{idx * 2!s:>2}: {line}'
            ))
            .to_tuple()
        ))
    )


def _pretty_format_code(code: Code) -> ResultME[Sequence[str]]:
    return (
        _pretty_format_opcodes_and_constants(code.opcodes, code.constants)
        .map(lambda opcodes_constants_strs: (
            iter2.chain(
                (
                    f'name: {code.name}',
                    f'flags: {code.flags}',
                    f'arg_count: {code.arg_count}',
                    f'pos_only_arg_count: {code.pos_only_arg_count}',
                    f'kw_only_arg_count: {code.kw_only_arg_count}',
                    f'locals_count: {code.locals_count}', 
                ),
                opcodes_constants_strs,
            )
            .to_tuple()
        ))
    )


def _pretty_format_opcodes_and_constants(opcodes: Sequence[OpCode], constants: Sequence[SupportedConstTypes]) -> ResultME[Sequence[str]]:
    pad_left_2 = lambda line: f'  {line}'
    return (
        collect_all_results((
            _pretty_format_opcodes(opcodes),
            _pretty_format_constants(constants),
        ))
        .map(with_packed_args(lambda opcodes_strs, constants_strs: (
            iter2.chain(
                ('opcodes:',),
                iter2(opcodes_strs).map(pad_left_2),
                ('constants:',),
                iter2(constants_strs).map(pad_left_2),
            )
            .to_tuple()
        )))
    )



def _pretty_format_constants(constants: Sequence[SupportedConstTypes]) -> ResultME[Sequence[str]]:
    return (
        iter2(constants)
        .map(_pretty_format_constant)
        .apply(collect_all_results)
        .map(lambda constant_str_seqs: (
            iter2(constant_str_seqs)
            .enumerate()
            .map_t(lambda idx, str_seq: (
                _label_multiline_with_shift(
                    f'{idx!s:>2}: ',
                    str_seq
                )
            ))
            .flatten()
            .to_tuple()
        ))
    )


def _pretty_format_constant(constant: SupportedConstTypes) -> ResultME[Sequence[str]]:
    if isinstance(constant, Code):
        return _pretty_format_code(constant)
    else:
        return (
            mdeserialize(constant)
            .map(repr)
            .map(lambda line: (line,))
        )


def _label_multiline_with_shift(label: str, lines: Sequence[str]) -> Sequence[str]:
    it = iter2(lines)
    first = it.next().unwrap_or('')
    return (
        iter2.chain(
            (f'{label}{first}',),
            it
            .map(lambda line: (
                f'  {line}'
            ))
        )
        .to_tuple()
    )


# ---

_format_solution = lambda source_lines, constants_lines: f"""
from bc_challenge.solutions.builders import create_patch_from_opcodes_and_constants


SOURCE = '''
{source_lines}
'''

CONSTANTS = (
{constants_lines}
)


SOLUTION = (
    create_patch_from_opcodes_and_constants(
        SOURCE, 
        CONSTANTS
    )
    .alt(lambda errs: repr(errs))
    .unwrap()
)

"""
