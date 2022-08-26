from bc_challenge.solutions.builders import create_patch_from_source


SOLUTION = create_patch_from_source('''
def sandbox():
    from bc_challenge.namespaces.vault import VAULT
    return VAULT['SECRET_IN_VAULT']
''').unwrap()


if __name__ == '__main__':
    from bc_challenge.misc.debug import pretty_print_code_patch
    pretty_print_code_patch(SOLUTION)
