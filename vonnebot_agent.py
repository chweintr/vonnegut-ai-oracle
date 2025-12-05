"""
Vonnebot LiveKit Agent with Simli Avatar
A Kurt Vonnegut-inspired reading companion powered by LiveKit + Simli + RAG
"""

import logging
import os
import json
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
import numpy as np
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.plugins import openai, simli

load_dotenv(override=True)

logger = logging.getLogger("vonnebot-agent")
logger.setLevel(logging.INFO)

# Paths
INDEX_PATH = Path("data/corpus_index.jsonl")
PROMPT_PATH = Path("prompts_base_prompt.txt")

# Load the Vonnegut system prompt
def load_system_prompt() -> str:
    """Load the base Vonnegut persona prompt."""
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "You are Kurt Vonnegut, the American author. Speak with wit and wisdom."


# RAG Knowledge Base Functions
def load_index() -> Dict:
    """Load the corpus index for RAG retrieval."""
    if not INDEX_PATH.exists():
        logger.warning("Corpus index not found at %s", INDEX_PATH)
        return {"embeddings": np.zeros((0, 0)), "chunks": []}

    embeddings: List[List[float]] = []
    chunks: List[Dict[str, str]] = []

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            chunks.append({
                "id": record.get("id"),
                "source": record.get("source"),
                "text": record.get("text"),
            })
            embeddings.append(record["embedding"])

    if not embeddings:
        return {"embeddings": np.zeros((0, 0)), "chunks": []}

    vectors = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = vectors / norms
    return {"embeddings": normalized, "chunks": chunks}


def search_corpus(query_embedding: List[float], top_k: int = 3) -> List[Dict[str, str]]:
    """Search the Vonnegut corpus using embedding similarity."""
    data = load_index()
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
        results.append({
            "score": float(scores[int(idx)]),
            "source": chunk["source"],
            "text": chunk["text"],
        })
    return results


# Build the full system prompt with RAG context
def build_prompt_with_context(user_message: str = None) -> str:
    """Build system prompt, optionally with RAG context."""
    base_prompt = load_system_prompt()

    # For now, return base prompt
    # RAG integration would require async embedding call
    # which we can add via a custom LLM wrapper later

    return base_prompt


# Main entrypoint
async def entrypoint(ctx: JobContext):
    """LiveKit agent entrypoint."""
    logger.info("Starting Vonnebot agent session")

    # Get credentials from environment
    simli_api_key = os.getenv("SIMLI_API_KEY")
    simli_face_id = os.getenv("SIMLI_FACE_ID")

    if not simli_api_key or not simli_face_id:
        logger.error("Missing SIMLI_API_KEY or SIMLI_FACE_ID")
        return

    # Load the Vonnegut system prompt
    system_prompt = build_prompt_with_context()

    # Create the agent session with OpenAI Realtime
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="ash",  # Options: alloy, ash, ballad, coral, echo, sage, shimmer, verse
            temperature=0.8,
            instructions=system_prompt,
        ),
    )

    # Configure Simli avatar
    simli_avatar = simli.AvatarSession(
        simli_config=simli.SimliConfig(
            api_key=simli_api_key,
            face_id=simli_face_id,
        ),
    )

    # Start the avatar session
    await simli_avatar.start(session, room=ctx.room)

    # Create the agent with Vonnegut instructions
    agent = Agent(
        instructions=system_prompt,
    )

    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
    )

    logger.info("Vonnebot agent is now active in room: %s", ctx.room.name)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM,
        )
    )
