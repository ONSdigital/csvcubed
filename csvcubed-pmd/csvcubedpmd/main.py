"""
PMD Tools CLI
-------------
"""
import argparse


from csvcubedpmd import codelist


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda _: ())
    subparsers = parser.add_subparsers(help="sub-commands")

    codelist.configure_argument_parser(
        subparsers.add_parser("codelist")
    )

    args = parser.parse_args()

    # Call the `set_defaults` function specified in the sub-parser.
    # This will handle execution of whatever needed to be done.
    args.func(args)


if __name__ == "__main__":
    main()
