from bc_challenge.solutions.builders import create_patch_from_opcodes_and_constants


SOURCE = '''
LOAD_CONST       1
LOAD_CONST       2
IMPORT_NAME      4
LOAD_ATTR        5      
RETURN_VALUE     
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

