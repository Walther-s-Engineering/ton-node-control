import click

main = click.Group()


@main.command()
def application() -> None:
    print('qqq')


if __name__ == '__main__':
    main()
