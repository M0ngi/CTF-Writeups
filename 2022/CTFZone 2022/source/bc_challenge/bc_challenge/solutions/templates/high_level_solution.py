from bc_challenge.solutions.builders import create_patch_from_source


SOLUTION = create_patch_from_source('''
def sandbox(arg):
    return 31337 
''').unwrap()


if __name__ == '__main__':
    from bc_challenge.misc.debug import pretty_print_code_patch
    pretty_print_code_patch(SOLUTION)
