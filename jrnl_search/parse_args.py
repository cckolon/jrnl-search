import argparse
from dataclasses import dataclass


def parse_args():
    parser = argparse.ArgumentParser(description='Search your jrnl.')
    parser.add_argument(
        'query',
        type=str,
        nargs='*',
        help='The search query',
        default=''
    )
    args = parser.parse_args()
    return Args(
        query=' '.join(args.query),
    )


@dataclass
class Args:
    query: str
