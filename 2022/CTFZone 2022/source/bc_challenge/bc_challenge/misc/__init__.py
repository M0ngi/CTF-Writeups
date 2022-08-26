
def with_packed_args(fn):
    def _wrapper(args):
        return fn(*args)
    return _wrapper
