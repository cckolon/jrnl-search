from rich.console import Console
from rich.table import Table


class ResultTable:
    def __init__(self, query: str):
        self.table = Table(
            title=f'Journal Entries Matching "{query}"',
            show_header=True
        )
        self.table.add_column("Similarity")
        self.table.add_column("Date/Time")
        self.table.add_column("Entry")

    def add_row(self, similarity, date, entry):
        self.table.add_row(similarity, date, entry)

    def print_table(self):
        console = Console()
        with console.pager():
            console.print(self.table)
