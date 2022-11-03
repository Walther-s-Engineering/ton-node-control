import click

from ton_node_control.utils.typing import Integer

main = click.Group()
wallet_commands = click.Group()


@main.command
def test() -> Integer:
    print('test')
    return 1


@wallet_commands.command
def test_2() -> Integer:
    print('test 2')
    return 1
