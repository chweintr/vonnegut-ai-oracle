"""Build a semantic index from Vonnegut source texts for retrieval-augmented prompting."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Iterable, List, Sequence

import openai

# Config defaults
DEFAULT_MODEL = "text-embedding-3-large"
DEFAULT_CHUNK_SIZE = 280  # words
DEFAULT_CHUNK_OVERLAP = 60  # words
INDEX_PATH = Path("data/corpus_index.jsonl")
MANIFEST_PATH = Path("data/corpus_manifest.json")

# Directories to scan by default
DEFAULT_SOURCE_DIRS = [
    Path("data/vonnegut_corpus"),
    Path("data/raw"),
    Path("data/excerpts"),
]


def iter_text_files(paths: Sequence[Path]) -> Iterable[Path]:
    """Yield .txt files from provided directories."""
    for base in paths:
        if not base.exists():
            continue
        if base.is_file() and base.suffix.lower() == ".txt":
            yield base
            continue
        for path in base.rglob("*.txt"):
            if path.name.startswith("."):
                continue
            yield path


def normalize_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            # Drop placeholder/instructional comments
            continue
        lines.append(stripped)
    return "\n".join(lines).strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        end = min(len(words), start + chunk_size)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
    return chunks


def batched(seq: Sequence[str], batch_size: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), batch_size):
        yield list(seq[i : i + batch_size])


def build_index(
    model: str,
    chunk_size: int,
    overlap: int,
    batch_size: int,
    source_dirs: Sequence[Path],
) -> None:
    client = openai.OpenAI()
    records = []

    for filepath in iter_text_files(source_dirs):
        raw_text = filepath.read_text(encoding="utf-8", errors="ignore")
        normalized = normalize_text(raw_text)
        chunks = chunk_text(normalized, chunk_size, overlap)
        try:
            rel_path = filepath.relative_to(Path.cwd())
        except ValueError:
            rel_path = filepath

        for idx, chunk in enumerate(chunks):
            records.append(
                {
                    "id": f"{filepath.stem}-chunk-{idx}",
                    "source": str(rel_path),
                    "text": chunk,
                }
            )

    if not records:
        raise SystemExit("No text chunks found. Check your data directories.")

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    with INDEX_PATH.open("w", encoding="utf-8") as index_file:
        for batch in batched(records, batch_size):
            inputs = [rec["text"] for rec in batch]
            response = client.embeddings.create(model=model, input=inputs)
            for rec, emb in zip(batch, response.data):
                rec_with_embedding = {
                    **rec,
                    "embedding": emb.embedding,
                    "model": model,
                }
                index_file.write(json.dumps(rec_with_embedding) + "\n")

    manifest = {
        "model": model,
        "chunk_size_words": chunk_size,
        "chunk_overlap_words": overlap,
        "total_chunks": len(records),
        "sources": sorted({rec["source"] for rec in records}),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Indexed {manifest['total_chunks']} chunks from {len(manifest['sources'])} files.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Vonnegut corpus embedding index")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI embedding model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in words (default: %(default)s)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help="Word overlap between chunks (default: %(default)s)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Embedding requests per batch (default: %(default)s)",
    )
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        help="Optional directory to include (can be passed multiple times). Defaults include data/vonnegut_corpus, data/raw, data/excerpts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    custom_dirs = [Path(src) for src in (args.sources or [])]
    source_dirs = custom_dirs or DEFAULT_SOURCE_DIRS

    missing = [str(path) for path in source_dirs if not path.exists()]
    if missing:
        print(f"⚠️ Warning: Skipping missing directories: {', '.join(missing)}")

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Export it before running this script.")

    build_index(
        model=args.model,
        chunk_size=args.chunk_size,
        overlap=args.chunk_overlap,
        batch_size=args.batch_size,
        source_dirs=source_dirs,
    )


if __name__ == "__main__":
    main()
