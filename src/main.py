from .cli.parser import create_cli


def main():
    # This creates all the necessary CLI components!
    cli = create_cli()
    cli()


if __name__ == "__main__":
    main()
