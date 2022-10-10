from bc_challenge.solutions.builders import create_patch_from_opcodes_and_constants


SOURCE = '''
LOAD_FAST      0
RETURN_VALUE
'''

CONSTANTS = (
    31337,
)


SOLUTION = (
    create_patch_from_opcodes_and_constants(
        SOURCE, 
        CONSTANTS
    )
    .alt(lambda errs: repr(errs))
    .unwrap()
)