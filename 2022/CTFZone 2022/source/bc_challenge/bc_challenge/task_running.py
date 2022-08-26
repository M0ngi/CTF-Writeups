from types import ModuleType
from typing import Mapping, Generator
from contextlib import contextmanager

from iter2 import iter2


from bc_challenge.misc.traceback import repack_exc_as_verbose_error

from bc_challenge.misc.result_ex import ResultME
from bc_challenge.code.model import CodePatch

from bc_challenge.namespaces.vault import VAULT


def run_task(*, task_source: str, patch: CodePatch, secret: str) -> ResultME[str]:
    config = _extract_config(task_source)
    run_kwargs = {} 

    if 'inject_secret_instead_of' in config:
        task_source = task_source.replace(
            config['inject_secret_instead_of'],
            secret
        )

    if 'put_secret_as_kwarg_with_name' in config:
        param_with_secret_name = config['put_secret_as_kwarg_with_name']
        run_kwargs[param_with_secret_name] = secret

    if 'put_secret_length_as_kwarg_with_name' in config:
        param_with_secret_length = config['put_secret_length_as_kwarg_with_name']
        run_kwargs[param_with_secret_length] = len(secret)

    if 'hide_secret_in_vault_with_name' in config:
        VAULT.clear()
        env_var_name = config['hide_secret_in_vault_with_name']
        VAULT[env_var_name] = secret

    persist_on_fs = 'persist_on_fs' in config

    if not persist_on_fs:
        load_module = _build_task_module
    else:
        load_module = _dump_to_fs_and_load


    with load_module(task_source) as task_module:
        try:
            return task_module.run(patch, **run_kwargs)
        except:
            return repack_exc_as_verbose_error()


# ---


def _extract_config(task_source: str) -> Mapping[str, str]:
    config_part = (
        iter2(task_source.split('\n'))
        .take_while(lambda line: line.startswith('# '))
        .map(lambda line: line[2:].lstrip())
        .join('\n')
    )

    from configparser import ConfigParser

    ini_parser = ConfigParser()
    ini_parser.read_string(config_part)

    return dict(ini_parser['TaskConfig'])


TEMP_TASK_MODULE_NAME = 'bc_challenge.namespaces.task_tmp'


@contextmanager
def _build_task_module(task_source: str) -> Generator[ModuleType, None, None]:
    import sys
    task_module = ModuleType(TEMP_TASK_MODULE_NAME)
    exec(task_source, task_module.__dict__)
    sys.modules[TEMP_TASK_MODULE_NAME] = task_module

    yield task_module

    del sys.modules[TEMP_TASK_MODULE_NAME]


@contextmanager
def _dump_to_fs_and_load(task_source: str) -> Generator[ModuleType, None, None]:
    import os
    import sys
    import importlib.util
    import tempfile
    from pathlib import Path

    tmp_py_root = tempfile.mkdtemp(prefix='py_root_')
    target_path = Path(tmp_py_root) / (TEMP_TASK_MODULE_NAME.replace('.', '/') + '.py')

    os.makedirs(target_path.parent, exist_ok=True)
    with open(target_path, 'w') as trgt:
        trgt.write(task_source)

    spec = importlib.util.spec_from_file_location(TEMP_TASK_MODULE_NAME, str(target_path))
    task_module = importlib.util.module_from_spec(spec)
    sys.modules[TEMP_TASK_MODULE_NAME] = task_module
    spec.loader.exec_module(task_module)

    yield task_module

    del sys.modules[TEMP_TASK_MODULE_NAME]
    os.unlink(target_path)
