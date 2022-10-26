import click
import subprocess

main = click.Group()


@click.group()
def main() -> None:
    pass


@main.command()
def update():
    print('Updating')


cli = click.CommandCollection(sources=[main])

if __name__ == '__main__':
    main()
