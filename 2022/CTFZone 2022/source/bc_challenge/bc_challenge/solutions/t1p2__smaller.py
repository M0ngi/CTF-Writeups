from bc_challenge.solutions.builders import create_patch_from_opcodes_and_constants


SOURCE = '''
LOAD_CONST       1
LOAD_CONST       2
IMPORT_NAME      4
IMPORT_FROM      5
LOAD_CONST       3
BINARY_SUBSCR    0
RETURN_VALUE     0
'''

CONSTANTS = (
    None,  # 0
    False,  # 1
    ('VAULT',),  # 2
    'SECRET_IN_VAULT',  # 3
    'bc_challenge.namespaces.vault',  # 4
    'VAULT',  # 5
    'VAULT',  # 6
)


SOLUTION = (
    create_patch_from_opcodes_and_constants(
        SOURCE, 
        CONSTANTS
    )
    .alt(lambda errs: repr(errs))
    .unwrap()
)

