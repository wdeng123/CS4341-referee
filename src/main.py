from .cli.parser import create_cli


def main():
    cli = create_cli()
    cli()


if __name__ == "__main__":
    main()
