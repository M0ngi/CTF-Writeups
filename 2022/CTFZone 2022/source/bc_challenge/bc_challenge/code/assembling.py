from typing import Tuple, Sequence, Union

import re
from dataclasses import dataclass

from iter2 import iter2

from returns.result import Result, safe, Success, Failure

from bc_challenge.misc.result_ex import ResultME, assert_not_none, resolve_failure, collect_all_results

from bc_challenge.code.model import OpCode


HumanReadableOpcode = Tuple[str, int]


def check_source_syntax(text: str) -> Tuple[Sequence[str], Sequence[Tuple[int, str]]]:
    lines_with_errors = []

    def _reg_errs(idx: int, errs: Sequence[InvalidOpcodeException]) -> str:
        for err in errs:
            lines_with_errors.append((idx, err.msg))
        return err.line

    def _render(line: Union[str, HumanReadableOpcode]) -> str:
        if isinstance(line, str):
            return line
        else:
            slug, arg = line
            return f'{slug!s:16} {arg}'

    reformated_opcode_lines = (
        iter2(text.splitlines())
        .map(_parse_opcode_line)
        .enumerate()
        .map_t(lambda idx, parse_result: (
            resolve_failure(
                parse_result,
                lambda errs: _reg_errs(idx, errs)
            )
        ))
        .map(_render)
        .to_tuple()
    )

    return reformated_opcode_lines, lines_with_errors


def assemble_source(text: str) -> Result[Sequence[OpCode], Sequence['InvalidOpcodeException']]:
    return (
        iter2(text.splitlines())
        .map(_parse_opcode_line)
        .enumerate()
        .map_t(lambda idx, parse_result: (
            parse_result
            .alt(lambda errs: (
                idx, errs
            ))
        ))
        .apply(collect_all_results)
        .bind(lambda lines: (
            iter2(lines)
            .filter(lambda line: not isinstance(line, str))
            .map_t(lambda slug, arg: (
                _assemble_opcode(slug)
                .map(lambda opcode: (
                    opcode, arg
                ))
                .alt(lambda err: (err,))  # never needed because of _parse_opcode_line
            ))
            .apply(collect_all_results)
            .map(tuple)
        ))
    )


def disassemble_opcodes(opcodes: Sequence[OpCode]) -> ResultME[Sequence[str]]:
    return (
        iter2(opcodes)
        .map_t(lambda opcode, arg: (
            _disassemble_opcode(opcode)
            .map(lambda slug: (
                slug, arg
            ))
            .alt(lambda err: (err,))
        ))
        .apply(collect_all_results)
        .map(lambda human_readable_opcodes: (
            iter2(human_readable_opcodes)
            .map_t(lambda slug, arg: (
                f'{slug!s:16} {arg}'
            ))
            .to_tuple()
        ))
    )


# ---


from opcode import opmap as OPCODE_MAPPING


REVERSE_OPCODE_MAPPING = {
    opcode: slug
    for slug, opcode in OPCODE_MAPPING.items()
}


def _validate_opcode(slug: str) -> Result[str, Exception]:
    if slug in OPCODE_MAPPING:
        return Success(slug)
    else:
        return Failure(Exception(f"Non-valid opcode: {slug}"))


def _assemble_opcode(slug: str) -> Result[str, Exception]:
    return (
        assert_not_none(
            OPCODE_MAPPING.get(slug),
            lambda: Exception(f"Non-valid opcode: {slug}"),
        )
    )


def _disassemble_opcode(opcode: int) -> Result[str, Exception]:
    return (
        assert_not_none(
            REVERSE_OPCODE_MAPPING.get(opcode),
            lambda: Exception(f"Non-valid opcode: {opcode}"),
        )
    )


_OPCODE_RX = re.compile(r'''^(?P<slug>\S+)(\s+(?P<arg>\S+))?$''')


@dataclass
class InvalidOpcodeException(Exception):
    msg: str
    line: str


def _parse_opcode(s: str) -> Result[HumanReadableOpcode, Sequence[InvalidOpcodeException]]:
    repack_error = lambda err: (
        InvalidOpcodeException(repr(err), s),
    )

    return (
        assert_not_none(
            _OPCODE_RX.match(s),
            lambda: (InvalidOpcodeException('Wrong syntax', s),)
        )
        .map(lambda m: m.groupdict())
        .bind(lambda md: (
            collect_all_results((
                _validate_opcode(md['slug'])
                .alt(repack_error),
                # ---
                safe(int)(md.get('arg') or 0)
                .alt(repack_error),
            ))
            .map(tuple)
        ))
    )


def _parse_opcode_line(s: str) -> Result[
    Union[str, HumanReadableOpcode],
    InvalidOpcodeException
]:
    s = s.strip()
    if len(s) == 0 or s.startswith('#'):
        return Success(s)
    else:
        return _parse_opcode(s)
