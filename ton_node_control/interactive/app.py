from simple_term_menu import TerminalMenu

from ton_node_control.interactive.menu.main import MainMenuEntries


def run() -> None:
    TerminalMenu(
        MainMenuEntries.choices(),
        title='Available commands'
    ).show()

