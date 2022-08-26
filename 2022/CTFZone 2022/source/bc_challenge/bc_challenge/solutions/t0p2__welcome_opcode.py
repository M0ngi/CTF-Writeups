from bc_challenge.solutions.builders import create_patch_from_opcodes_and_constants


SOURCE = '''
LOAD_FAST      0
RETURN_VALUE   0
'''

CONSTANTS = (
    'arg',
)


SOLUTION = (
    create_patch_from_opcodes_and_constants(
        SOURCE, 
        CONSTANTS
    )
    .alt(lambda errs: repr(errs))
    .unwrap()
)
