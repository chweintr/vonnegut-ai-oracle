"""Lightweight retrieval helper for Vonnegut corpus."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np

INDEX_PATH = Path("data/corpus_index.jsonl")


def index_available() -> bool:
    return INDEX_PATH.exists()


@lru_cache(maxsize=1)
def _load_index() -> Dict[str, np.ndarray]:
    if not INDEX_PATH.exists():
        return {"embeddings": np.zeros((0, 0)), "chunks": []}

    embeddings: List[List[float]] = []
    chunks: List[Dict[str, str]] = []

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            chunks.append(
                {
                    "id": record.get("id"),
                    "source": record.get("source"),
                    "text": record.get("text"),
                }
            )
            embeddings.append(record["embedding"])

    if not embeddings:
        return {"embeddings": np.zeros((0, 0)), "chunks": []}

    vectors = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = vectors / norms
    return {"embeddings": normalized, "chunks": chunks}


def search_by_embedding(query_embedding: List[float], top_k: int = 3) -> List[Dict[str, str]]:
    data = _load_index()
    embeddings = data["embeddings"]
    chunks = data["chunks"]

    if embeddings.size == 0:
        return []

    query_vec = np.array(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(query_vec)
    if q_norm == 0:
        return []
    query_vec = query_vec / q_norm

    scores = embeddings @ query_vec
    if top_k >= len(chunks):
        top_indices = np.argsort(scores)[::-1]
    else:
        top_indices = np.argpartition(scores, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

    results = []
    for idx in top_indices:
        chunk = chunks[int(idx)]
        results.append(
            {
                "score": float(scores[int(idx)]),
                "source": chunk["source"],
                "text": chunk["text"],
            }
        )
    return results


def clear_cache() -> None:
    _load_index.cache_clear()
