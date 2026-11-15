"""Stage 3 and 4: embed the chunks, store them, and search them.

YOUR CODE GOES HERE. `Hit` and the OpenAI client are written for you, because
plumbing is not the lesson. `embed_texts`, `cosine_similarity`, `build_index`
and `search` are the lesson.
"""

from dataclasses import dataclass
import hashlib, os

import numpy as np
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"

_cached: OpenAI | None = None


def client() -> OpenAI:
    """The OpenAI client, built on first use and reused after that.

    It is built lazily, not at import time, so that .env has already been
    loaded by the time it looks for OPENAI_API_KEY.
    """
    global _cached
    if _cached is None:
        _cached = OpenAI()
    return _cached


@dataclass
class Hit:
    """One retrieved chunk, and everything you need to cite it.

    `chunk_id` is what makes an answer traceable: when an answer is wrong in
    Week 4, this is how you find out which chunk caused it. Keep it.
    """

    chunk_id: int
    text: str
    score: float

    def citation(self) -> str:
        """A short, human-readable label for this chunk. Printed under answers."""
        preview = " ".join(self.text.split())[:60]
        return f"[chunk {self.chunk_id}] {preview}... (score {self.score:.3f})"


def embed_texts(texts: list[str]) -> np.ndarray:
    """Turn a list of strings into a matrix of embedding vectors.

    Args:
        texts: the strings to embed. One API call can take many at once —
            do NOT loop and call once per chunk.

    Returns:
        An array of shape (len(texts), 1536), one row per input string,
        in the same order as `texts`.

    Hint: `client().embeddings.create(input=texts, model=EMBEDDING_MODEL)`.
    The response has a `.data` list; each item has an `.embedding`. Wrap the
    result in np.array(). Print `response.usage` once — knowing what a corpus
    costs to embed is the number that decides architecture at scale.
    """
    embedding_result = client().embeddings.create(input=texts, model=EMBEDDING_MODEL)
    print("Usage: ", embedding_result.usage)
    return np.array([embedding_data.embedding for embedding_data in embedding_result.data])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """How similar are two vectors? 1.0 is identical, 0.0 is unrelated.

    Hint: the dot product, divided by the product of the two norms.
    NumPy has `np.dot` and `np.linalg.norm`.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def build_index(chunks: list[str]) -> np.ndarray:
    """Embed every chunk once, and return the matrix to search against.

    Args:
        chunks: from corpus.split_corpus().

    Returns:
        The embedding matrix. Row i corresponds to chunks[i] — that
        correspondence is the only thing holding your citations together,
        so do not sort or filter one without the other.

    Hint: this is mostly a call to embed_texts(). Notice that it happens once
    per process, and that a fresh process has no memory of the last one.
    """
    # This is my main improvement - caching the embeddings on disk in order to avoid spending tokens to re-embed chunks
    # In order to avoid stale files if the chunking or model change, we need to create a hash from the chunks + model name
    h = hashlib.sha256()
    h.update(EMBEDDING_MODEL.encode("utf-8"))
    for chunk in chunks:
        h.update(b"\x00")
        h.update(chunk.encode("utf-8"))
    key = h.hexdigest()[:16]
    save_file_subname = f"embeddings_{key}"
    save_file_name = f"{save_file_subname}.npy"

    if os.path.isfile(save_file_name):
        return np.load(save_file_name)
    else:
        embeddings = embed_texts(chunks)
        np.save(save_file_subname, embeddings)
        return embeddings

    # return embed_texts(chunks)


def search(query: str, chunks: list[str], matrix: np.ndarray, k: int = 3) -> list[Hit]:
    """Find the k chunks most similar to the query.

    Args:
        query: the user's question, as typed.
        chunks: the chunk texts.
        matrix: the embedding matrix from build_index().
        k: how many hits to return.

    Returns:
        Up to k Hits, most similar first.

    Hints:
      - Embed the query with the SAME model you built the index with. A query
        embedded by a different model is not comparable, and the failure is
        silent — you get plausible-looking nonsense, not an error.
      - Score the query against every row, then sort.
      - Read the signature again: it says "up to k". Nothing here forces you to
        return exactly k. That freedom is the whole of Step 4's threshold option.
    """
    embedded_query = embed_texts([query])[0]
    scored_chunks = []
    for i, embedded_chunk in enumerate(matrix):
        similarity = cosine_similarity(embedded_query, embedded_chunk)
        scored_chunks.append(Hit(i, chunks[i], similarity))
    scored_chunks.sort(key=lambda hit: hit.score, reverse=True)
    return scored_chunks[:k]
