"""Print the effective retry profile for each service."""

import argparse
import sys

from config import resolve_profile, resolved_profile_name
from services import SERVICES


def rows():
    for name in sorted(SERVICES):
        explicit = SERVICES[name]["profile"]
        profile = resolve_profile(explicit)
        yield name, resolved_profile_name(explicit), profile["attempts"]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Show effective retry profiles.")
    parser.parse_args(argv)
    for name, profile_name, attempts in rows():
        print(f"{name:10} {profile_name:14} attempts={attempts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
