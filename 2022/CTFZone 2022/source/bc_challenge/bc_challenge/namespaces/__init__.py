def clear_module_meta(module):
    module.__builtins__ = None
    module.__loader__ = None
    module.__spec__ = None


# TODO: update for any new namespace
from . import empty
from . import vault


NAMESPACE_MODULES = [
    empty,
    vault,
]

for module in NAMESPACE_MODULES:
    clear_module_meta(module)


__builtins__ = None
__loader__ = None
__spec__ = None
