import typing as t
import subprocess
import pkg_resources

import click

from subprocess import call

from ton_node_control.cli.utils.messages import message
from ton_node_control.utils.typing import String, Integer


OPERATION_NOT_PERMITTED: t.Final[Integer] = 1

main = click.Group()


@click.group()
def main() -> None:
    pass


@main.command()
def update():
    message(
        'Updating "ton_node_control" and following packages:\n'
        + '\n'.join(f'\t{package}' for package in pkg_resources.working_set),
    )
    must_proceed: bool = click.prompt(
        type=bool,
        text='Continue?',
        prompt_suffix=' ',
    )
    if must_proceed is True:
        for dist in pkg_resources.working_set:
            package, _ = str(dist).split(' ')
            package: String
            exit_code: Integer = call(
                'python -m pip install '
                '--ignore-installed '
                f'--upgrade {package}',
                shell=True,
            )
            if exit_code == OPERATION_NOT_PERMITTED:
                raise message(
                    f'Failed to update package "{package}" '
                    f'with "pip". Exit code: "{exit_code}"',
                    exit_after=True,
                )
            raise message('Update successfully process completed.', exit_after=True)
    raise message('Updated aborted.', exit_after=True)
    

cli = click.CommandCollection(sources=[main])

if __name__ == '__main__':
    main()
