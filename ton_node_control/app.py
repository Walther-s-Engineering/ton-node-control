import sys
import typing as t

import click

import ton_node_control

main = click.Group()


def exit_callback(context, parameter, value) -> None:
    print(vars(context))
    print(value)
    sys.exit(1)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click.option(
    '-i',
    '--interactive',
    # callback=exit_callback,
    default=False,
    type=bool,
    is_flag=True,
    help='Run "ton-node-controller" in interactive mode.',
)
def app(interactive: bool = False) -> None:
    if interactive is True:
        raise NotImplementedError
    ton_node_control.interactive_app.run()

