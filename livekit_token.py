"""
LiveKit Token Generation for Vonnebot
Generates access tokens for frontend clients to connect to LiveKit rooms.
"""

import os
import time
from livekit import api


def generate_token(room_name: str = "vonnebot-room", participant_name: str = "user") -> str:
    """
    Generate a LiveKit access token for a participant to join a room.

    Args:
        room_name: Name of the room to join
        participant_name: Name/identity of the participant

    Returns:
        JWT token string
    """
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")

    token = api.AccessToken(api_key, api_secret)
    token.with_identity(participant_name)
    token.with_name(participant_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
    ))

    # Token valid for 1 hour
    token.with_ttl(3600)

    return token.to_jwt()


def get_livekit_url() -> str:
    """Get the LiveKit server URL from environment."""
    url = os.getenv("LIVEKIT_URL")
    if not url:
        raise ValueError("LIVEKIT_URL must be set")
    return url


if __name__ == "__main__":
    # Test token generation
    from dotenv import load_dotenv
    load_dotenv()

    token = generate_token()
    print(f"Token: {token[:50]}...")
    print(f"URL: {get_livekit_url()}")
