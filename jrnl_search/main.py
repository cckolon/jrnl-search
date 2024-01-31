from jrnl_search.search import search
from .parse_args import parse_args


def run():
    args = parse_args()
    query = args.query
    if not query:
        query = input('Please enter a query')
    search(query)
