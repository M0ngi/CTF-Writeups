from iter2 import iter2

from returns.functions import raise_exception, tap
from returns.converters import maybe_to_result
from returns.result import safe, Success, Failure

import click

from bc_challenge.code.model import CodePatch
from bc_challenge.misc import with_packed_args
from bc_challenge.misc.result_ex import collect_all_results

from .settings import ClientSettings
from bc_challenge.misc.settings import load_settings, dump_settings

from bc_challenge.api.client import ApiClient

from bc_challenge import testing
from bc_challenge.secret import Secret, search_secret_in_text

from bc_challenge.misc.debug import pretty_print_code_patch, print_code_patch_as_python_code


client_settings = (
    load_settings(ClientSettings, 'client_settings.yaml')
    .alt(raise_exception)
    .unwrap()
)

api_client = ApiClient(
    api_url=client_settings.api.url,
    team_token=client_settings.api.team_token,
)


@click.group()
def cli():
    ...


@cli.command()
@click.argument('task_name')
def x_download_source(task_name: str):
    '''Manually download task source code'''
    (
        _download_source(task_name)
        .map(lambda source: (
            click.echo(source)
        ))    
    )

@cli.command()
@click.argument('task_name')
def submit_solution(task_name: str):
    '''Submit solution for secret'''
    echo_info(f'Testing: {task_name}') 
    verdict, result = testing.test_solution(task_name)
    if verdict:
        echo_success('Solution works locally')
    else:
        echo_failure('Solution doesn\'t work. Every challenge can be solved reflecting secret')
        click.echo('---')
        click.echo(result)
        return

    access_code = ( 
        _retrieve_access_code(task_name)
        .map(tap(lambda access_code: (
            echo_info(f'Using access code "{access_code}" to submit task solution: "{task_name}"')
        )))
        .alt(on_new_error(lambda _: (
            echo_failure(f'No access code for this task: {task_name}')
        )))
    )

    solution = (
        _read_solution(task_name)
        .alt(on_new_error(lambda err: (
            echo_failure(f'No solution for this task: {task_name}\n{err!r}')
        )))
    ) 

    (
        collect_all_results((
            access_code,
            solution,
        ))
        .map(tap(lambda _: (
            echo_info('Submitting solution...')
        )))
        .bind(with_packed_args(lambda access_code, solution: (
            api_client.submit_solution(
                task_name,
                access_code,
                solution,
            )
        )))
        .alt(on_new_error(lambda err: (
            echo_failure(f'Submission was not successful\n{err!r}')
        )))
        .map(tap(lambda result: (
            echo_success(f'Submission was successful')
        )))

        .bind(lambda result: (
            maybe_to_result(
                search_secret_in_text(result),
            )
            .alt(lambda none: result)
        ))
        .alt(on_new_error(lambda result: (
            echo_failure(f'Secret not found in result\n---\n{result}')
        )))

        .bind(lambda secret: (
            _process_secret(secret)
        ))

        .bind(lambda secret: (
            _persist_client_settings()
            .map(lambda _: secret)
        ))

        .bind(lambda secret: (
            Success(secret.next_task.name)
            if secret.next_task is not None
            else Failure(Exception('No next task!'))
        ))
        .alt(on_new_error(lambda _: (
            echo_success('No next task, last was the final! Congrats!')
        )))

        .bind(lambda next_task_name: (
            _download_source(next_task_name)
            .bind(lambda source: (
                _persist_task_source(
                    next_task_name,
                    source,
                )
            ))
            .map(tap(lambda _: (
                echo_success(f'Successfully persisted task source: "{next_task_name}"')
            )))
            .alt(on_new_error(lambda err: (
                echo_failure(f'Failed to persist task source on disk. Try to do it manually with "download-source" command\n{err!r}')
            )))
        ))
    )


@cli.command()
@click.argument('task_name')
@click.option('--as-py-code', is_flag=True, default=False, help='Dump in format convenient for copy')
def view_solution(task_name: str, as_py_code: bool):
    '''Pretty print solution (opcodes and constants)'''
    (
        _read_solution(task_name)
        .alt(on_new_error(lambda err: (
            echo_failure(f'No solution for this task: {task_name}\n{err!r}')
        )))
        .map(lambda solution: (
            echo_success(f'Solution successfully loaded for task: {task_name}'),   
            pretty_print_code_patch(solution) if not as_py_code
            else print_code_patch_as_python_code(solution),
        ))
    )


@cli.command()
@click.argument('task_name')
def test_solution(task_name: str):
    '''Test that solution reflects fake secret'''
    echo_info(f'Testing: {task_name}') 
    verdict, result = testing.test_solution(task_name)
    if verdict:
        echo_success('Secret was found in result!')
    else:
        echo_failure('Secret was NOT found in result')
    click.echo('---')
    click.echo(result)


@cli.command()
@click.argument('secret') 
def x_process_secret(secret: str):
    '''Unpack and process secret in format: "SECRET{...}"'''
    (
        _process_secret(secret)
        .bind(lambda _: (
            _persist_client_settings()
        ))
    )


@cli.command()
def x_view_findings():
    '''List access codes and flags'''
    list_items = lambda d: (
        iter2(d.items())
        .map_t(lambda task_name, flag: (
            f'{task_name}: {flag}'
        ))
        .foreach(lambda s: (
            click.echo(f'- {s}')
        ))
    )

    flags = client_settings.findings.flags
    if len(flags) > 0:
        echo_titled('FLAGS', '')
        list_items(flags)
        

    access_codes = client_settings.findings.tasks_access_codes
    if len(access_codes) > 0:
        echo_titled('ACCESS_CODES', '')
        list_items(access_codes)


# ---

def on_new_error(fn):
    def _wrapper(err):
        return (
            fn(err) if err is not None else None
        )
    return _wrapper

def echo_titled(title, message, color='white'):
    click.echo(
        click.style(f'{title}: ', fg=color, bold=True),
        nl=False
    )
    click.echo(message)


def echo_good(title, message):
    return echo_titled(title, message, 'green')


def echo_bad(title, message):
    return echo_titled(title, message, 'red')


def echo_info(message):
    return echo_titled('[*]', message)


def echo_success(message):
    return echo_good('[*]', message)


def echo_failure(message):
    return echo_bad('[!]', message)

# ---

@safe
def _retrieve_access_code(task_name: str) -> str:
    return client_settings.findings.tasks_access_codes[task_name]


@safe
def _read_solution(task_name: str) -> CodePatch:
    from importlib import import_module
    return import_module('bc_challenge.solutions.' + task_name).SOLUTION


@safe
def _persist_task_source(task_name: str, source: str) -> None:
    with open(f'./bc_challenge/tasks/{task_name}.py', 'w') as f:
        f.write(source)


def _download_source(task_name: str):
    return (
        _retrieve_access_code(task_name)
        .map(tap(lambda access_code: (
            echo_info(f'Using access code "{access_code}" to download task source: "{task_name}"')
        )))
        .alt(on_new_error(lambda _: (
            echo_failure(f'No access code for this task: {task_name}')
        )))
        
        .bind(lambda access_code: (
            api_client.download_task_source(
                task_name,
                access_code,
            )
        ))
        .map(tap(lambda _: (
            echo_success(f'Sources for task "{task_name}" successfully downloaded')
        )))
        .alt(on_new_error(lambda err: (
            echo_failure(err)
        )))
    )


def _process_secret(secret: str):
    flags = client_settings.findings.flags
    tasks_access_codes = client_settings.findings.tasks_access_codes

    def _save_flag(secret: Secret):
        if secret.flag is not None:
            flags[secret.task_name] = secret.flag
            echo_success(f'Flag saved: ' + click.style(secret.flag, bold=True))

    def _save_access_code(secret: Secret):
        next_task = secret.next_task
        if next_task is not None:
            tasks_access_codes[next_task.name] = next_task.access_code
            echo_success(f'Access code for "{next_task.name}" saved: ' + click.style(next_task.access_code, bold=True))


    return (
        Secret.unpack(secret)
        .map(tap(lambda secret: (
            echo_success(f'Parsed valid secret: {secret}')
        )))
        .alt(on_new_error(lambda err: (
            echo_failure(f'Failed to parse secret: {secret}\n{err!r}')
        )))

        .map(tap(_save_flag))
        .map(tap(_save_access_code))
    )


def _persist_client_settings():
    return (
        dump_settings(client_settings, 'client_settings.yaml')
        .map(lambda _: (
            echo_good('[*]', 'Client settings and findings persisted')
        ))
        .alt(lambda err: (
            echo_failure('Failed to persist client settings and findings\n{err!r}')
        ))
    )
