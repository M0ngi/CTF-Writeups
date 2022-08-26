from iter2 import iter2

from bc_challenge.code.opcodes import OPCODE_MAPPING


MODEL_TO_NATIVE_MAPPING = {
    'name': 'co_name',
    'flags': 'co_flags',
    'arg_count': 'co_argcount',
    'pos_only_arg_count': 'co_posonlyargcount',
    'kw_only_arg_count': 'co_kwonlyargcount',
    'locals_count': 'co_nlocals',
}

NATIVE_TO_MODEL_MAPPING = (
    {
        native: model
        for model, native in MODEL_TO_NATIVE_MAPPING.items()
    }
    |
    {
        'co_filename': 'name',
    }

)

NATIVE_POHUI_FIELDS_CONSTANTS = {
    'co_firstlineno': 1,
    'co_lnotab': b'',
    'co_stacksize': 7,
}


_CONSTANTS_USAGE_MAPPING_STR = {
    'co_consts': ('LOAD_CONST',),
    'co_names': (
        'STORE_NAME', 'LOAD_NAME', 'DELETE_NAME',
        'STORE_ATTR', 'LOAD_ATTR', 'DELETE_ATTR',
        'LOAD_METHOD',
        'IMPORT_NAME', 'IMPORT_FROM'
    ),
    'co_varnames': ('STORE_FAST', 'LOAD_FAST', 'DELETE_FAST'),
}

CONSTANTS_USAGE_MAPPING = (
    iter2(_CONSTANTS_USAGE_MAPPING_STR.items())
    .map_t(lambda attr, opcode_strs: (
        attr, 
        iter2(opcode_strs).map(OPCODE_MAPPING.__getitem__).to_tuple()
    ))
    .to_dict()
)
