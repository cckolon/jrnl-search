import asyncio
import json
import os
from dataclasses import dataclass
from functools import cache, cached_property
from hashlib import sha256
from typing import Optional

import numpy as np
from jrnl.install import load_or_install_jrnl
from jrnl.journals import Entry, Journal
from sentence_transformers import SentenceTransformer
from .display import ResultTable


@cache
def jrnl_config():
    return load_or_install_jrnl(None)


@cache
def jrnl_location():
    return jrnl_config()['journals']['default']['journal']


@cache
def embedding_location():
    journal_directory = os.path.dirname(jrnl_location())
    journal_name = os.path.basename(jrnl_location())
    return os.path.join(journal_directory, f'.{journal_name}_embeddings.json')


@dataclass
class EmbeddedEntry:
    entry: Entry
    embedding: Optional[np.array] = None
    query_similarity: Optional[float] = None

    @cached_property
    def hash(self) -> str:
        return sha256(self.entry.text.encode("utf-8")).hexdigest()

    def similarity(self, embedding: np.array) -> float:
        if self.embedding is None:
            raise ValueError('Entry has no embedding')
        return np.dot(self.embedding, embedding)


def load_journal_to_entries(location: str) -> list[EmbeddedEntry]:
    j = Journal()
    j.open(location)
    return [
        EmbeddedEntry(entry=entry)
        for entry in j.entries
    ]


def load_embeddings(
    location: str,
    entries: list[EmbeddedEntry]
):
    if not os.path.exists(location):
        return
    with open(location, 'r', encoding='utf-8') as f:
        embeddings_dict: dict = json.loads(f.read())  # hash: embedding
    for entry in entries:
        if embedding := embeddings_dict.get(entry.hash):
            entry.embedding = np.array(embedding)


async def generate_remaining_embeddings(
    entries: list[EmbeddedEntry],
    model: SentenceTransformer,
):
    unembedded_entries = [
        entry for entry in entries
        if entry.embedding is None
    ]
    if len(unembedded_entries) == 0:
        return
    unembedded_texts = [entry.entry.text for entry in unembedded_entries]
    unembedded_embeddings = model.encode(unembedded_texts)
    for entry, embedding in zip(unembedded_entries, unembedded_embeddings):
        entry.embedding = embedding


async def generate_query_embedding(
    query: str,
    model: SentenceTransformer
) -> np.array:
    embedding = model.encode([query])[0]
    return embedding


def sort_by_similarity(
    query_embedding: np.array,
    entries: list[EmbeddedEntry],
) -> list[EmbeddedEntry]:
    for entry in entries:
        entry.query_similarity = entry.similarity(query_embedding)
    return sorted(
        entries,
        key=lambda entry: entry.query_similarity,
        reverse=True
    )


def save_embeddings(
    location: str,
    entries: list[EmbeddedEntry]
) -> None:
    for entry in entries:
        if entry.embedding is None:
            raise ValueError('Not all entries have embeddings')
    with open(location, 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            entry.hash: entry.embedding.tolist()
            for entry in entries
        }))


async def load_model():
    model = SentenceTransformer(
        'sentence-transformers/multi-qa-mpnet-base-dot-v1'
    )
    return model


async def async_search(query: str):
    model = asyncio.create_task(load_model())
    entries = load_journal_to_entries(jrnl_location())
    load_embeddings(embedding_location(), entries)
    embed_task = asyncio.create_task(generate_remaining_embeddings(
        entries,
        await model
    ))
    query_embedding = asyncio.create_task(
        generate_query_embedding(
            query,
            await model
        )
    )
    await embed_task
    save_embeddings(embedding_location(), entries)
    entries = sort_by_similarity(await query_embedding, entries)
    results = ResultTable(query)
    for entry in entries:
        results.add_row(
            str(round(entry.query_similarity, 6)),
            str(entry.entry.date),
            entry.entry.text,
        )
    results.print_table()


def search(query: str):
    asyncio.run(async_search(query))
