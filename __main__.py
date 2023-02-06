import sys

from ton_node_control.cli.app import main

if __name__ == '__main__':
    sys.exit(main(standalone_mode=False))
