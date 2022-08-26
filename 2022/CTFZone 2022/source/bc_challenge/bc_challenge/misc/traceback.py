import sys

from iter2 import iter2
from returns.result import Success

from IPython.core.ultratb import VerboseTB


VERBOSE_FORMATTER = VerboseTB(
    color_scheme='NoColor',
    include_vars=False,
)

VERBOSE_FORMAT_EXC = VERBOSE_FORMATTER.format_exception_as_a_whole


def verbose_traceback(context_size: int = 3) -> str:
    return (
        iter2(
            VERBOSE_FORMAT_EXC(
                *sys.exc_info(), 
                context_size, 
                None
            )
        )
        .flatten()
        .join('\n')
    )


def repack_exc_as_verbose_error() -> Success[str]:
    return Success(
        verbose_traceback()
    )