import sys

from ton_node_control.cli.app import main, cmds

if __name__ == '__main__':
    sys.exit(cmds(standalone_mode=False))
