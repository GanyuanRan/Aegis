"""Inventory command line."""

import argparse
import sys

from export import export_json
from fixtures import FIXTURES


def main(argv=None):
    parser = argparse.ArgumentParser(prog="inventory")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("export", help="print the partner JSON feed")
    args = parser.parse_args(argv)
    if args.command == "export":
        print(export_json(FIXTURES))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
