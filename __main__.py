import sys

import click

import ton_node_control

if __name__ == '__main__':
    cli = click.CommandCollection(sources=[ton_node_control.app.main, ton_node_control.app.wallet_commands])
    sys.exit(cli())
