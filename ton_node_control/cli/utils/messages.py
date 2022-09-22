import typing as t

import click


def message(text: str, exit_after=True) -> t.Optional[SystemExit]:
    click.secho(text)
    if exit_after is True:
        return SystemExit(0)


def error(text: str) -> SystemExit:
    click.secho(text, fg='red')
    return SystemExit(1)
