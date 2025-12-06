# -*- coding: utf-8 -*-
"""
Vonnebot: A Kurt Vonnegut Inspired Reading Companion
Flask backend with beautiful typewriter-style frontend
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import openai
import requests
import os
import time
import uuid
import json
import random
from pathlib import Path
from dotenv import load_dotenv

# LiveKit import - optional, only needed if using LiveKit
try:
    from livekit import api as livekit_api
except ImportError:
    livekit_api = None

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Simli configuration
SIMLI_API_KEY = os.getenv("SIMLI_API_KEY")
SIMLI_AGENT_ID = os.getenv("SIMLI_AGENT_ID")
SIMLI_FACE_ID = os.getenv("SIMLI_FACE_ID")

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Load Vonnegut system prompt
PROMPT_PATH = Path("prompts_base_prompt.txt")
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "You are Kurt Vonnegut."

# Available texts
TEXTS_DIR = Path("data/vonnegut_corpus/public_domain")
AVAILABLE_TEXTS = {}

if TEXTS_DIR.exists():
    for txt_file in TEXTS_DIR.glob("*.txt"):
        # Create readable name from filename
        name = txt_file.stem.replace("_", " ")
        # Add year if known
        years = {
            "2BR02B": "2BR02B (1962)",
            "HarrisonBergeron": "Harrison Bergeron (1961)",
            "TheBigTripUpYonder": "The Big Trip Up Yonder (1954)",
        }
        display_name = years.get(txt_file.stem, name)
        AVAILABLE_TEXTS[display_name] = txt_file

# Load doodle manifest
DOODLES_MANIFEST_PATH = Path("static/doodles/manifest.json")
DOODLES = []
if DOODLES_MANIFEST_PATH.exists():
    try:
        DOODLES = json.loads(DOODLES_MANIFEST_PATH.read_text(encoding="utf-8")).get("doodles", [])
    except Exception:
        pass


def check_for_doodle(message: str) -> dict | None:
    """
    Check if the user's message should trigger a doodle response.
    Returns doodle info dict or None.
    """
    message_lower = message.lower()

    for doodle in DOODLES:
        triggers = doodle.get("triggers", [])
        random_chance = doodle.get("random_chance", 0.1)

        # Check if any trigger words are in the message
        for trigger in triggers:
            if trigger.lower() in message_lower:
                # Roll for random chance (so not every trigger returns a doodle)
                if random.random() < random_chance:
                    return {
                        "image": doodle["image"],
                        "alt": doodle.get("alt", ""),
                        "caption": doodle.get("caption")
                    }

    return None


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route('/')
def index():
    """Serve the main page."""
    return render_template(
        'index.html',
        texts=list(AVAILABLE_TEXTS.keys()),
        simli_agent_id=SIMLI_AGENT_ID,
        livekit_url=LIVEKIT_URL
    )


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


@app.route('/api/texts')
def get_texts():
    """Return list of available texts."""
    return jsonify(list(AVAILABLE_TEXTS.keys()))


@app.route('/api/text/<text_name>')
def get_text(text_name):
    """Return the content of a specific text."""
    if text_name not in AVAILABLE_TEXTS:
        return jsonify({"error": "Text not found"}), 404

    path = AVAILABLE_TEXTS[text_name]
    if not path.exists():
        return jsonify({"error": "File not found"}), 404

    content = path.read_text(encoding="utf-8")

    # Split into paragraphs for better rendering
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    return jsonify({
        "title": text_name,
        "paragraphs": paragraphs,
        "raw": content
    })


@app.route('/api/simli-token', methods=['POST'])
def get_simli_token():
    """Generate a Simli session token."""
    if not SIMLI_API_KEY:
        return jsonify({"error": "Simli API key not configured"}), 500

    try:
        response = requests.post(
            "https://api.simli.ai/getToken",
            json={"apiKey": SIMLI_API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "token": data.get("token"),
            "agentId": SIMLI_AGENT_ID,
            "faceId": SIMLI_FACE_ID
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/livekit-token', methods=['POST'])
def get_livekit_token():
    """Generate a LiveKit token for the user to join a room."""
    if not livekit_api or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return jsonify({"error": "LiveKit not configured"}), 500

    # Create a unique room name and user identity
    room_name = f"vonnebot-{uuid.uuid4().hex[:8]}"
    user_identity = f"user-{uuid.uuid4().hex[:8]}"

    # Create access token
    token = livekit_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(user_identity)
    token.with_name("Reader")
    token.with_grants(livekit_api.VideoGrants(
        room_join=True,
        room=room_name,
    ))

    return jsonify({
        "token": token.to_jwt(),
        "room": room_name,
        "identity": user_identity,
        "url": LIVEKIT_URL
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.json
    user_message = data.get('message', '')
    visible_context = data.get('context', '')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Check if this should trigger a doodle response
    doodle = check_for_doodle(user_message)
    if doodle:
        return jsonify({"doodle": doodle})

    if not openai_client:
        return jsonify({
            "response": "OpenAI API key not configured. So it goes."
        })

    # Build messages for the API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add context about what user is currently reading
    if visible_context:
        context_msg = f"""
The reader is currently looking at this passage:

---
{visible_context[:2000]}
---

Keep this context in mind when responding. You can reference it naturally without the user having to point it out.
"""
        messages.append({"role": "system", "content": context_msg})

    # Add chat history (last 6 exchanges)
    for msg in chat_history[-12:]:
        role = "user" if msg.get("type") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": user_message})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=600,
            temperature=0.8,
        )
        return jsonify({
            "response": response.choices[0].message.content.strip()
        })
    except Exception as e:
        return jsonify({
            "response": f"I seem to be having trouble. So it goes. ({str(e)})"
        })


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
