# Jrnl Search: A Semantic Search Engine for [Jrnl](https://jrnl.sh/)

## Installation

- [Install python 3.10 or higher if you don't already have it](https://wiki.python.org/moin/BeginnersGuide/Download).
- [Install pipx](https://pipx.pypa.io/stable/installation/).
- [Install jrnl](https://jrnl.sh/en/stable/installation/).
- Install jrnl-search: `$ pipx install jrnl-search` (this takes a while since it installs some beefy ML libraries).

## Usage

- Make some jrnl entries:
  - `$ jrnl this entry is about bats`
  - `$ jrnl this entry is not`
- Search for them (the first search may take a while since the models have to download):
  - `$ jrnl-search flying animals`
