# -*- coding: utf-8 -*-
"""
Vonnebot: A Kurt Vonnegut Inspired Reading Companion
Flask backend with beautiful typewriter-style frontend
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import openai
import requests
import os
import time
import uuid
import json
import random
import re
import base64
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

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

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
    """Generate a Simli session token using the new /auto/token endpoint."""
    if not SIMLI_API_KEY:
        return jsonify({"error": "Simli API key not configured"}), 500

    try:
        response = requests.post(
            "https://api.simli.ai/auto/token",
            headers={"Content-Type": "application/json"},
            json={
                "simliAPIKey": SIMLI_API_KEY,
                "expiryStamp": -1,
                "llmAPIKey": "",
                "ttsAPIKey": "",
                "originAllowList": [],
                "createTranscript": False
            }
        )
        response.raise_for_status()
        data = response.json()
        return jsonify({
            "token": data.get("token") or data.get("sessionToken"),
            "agentId": SIMLI_AGENT_ID,
            "faceId": SIMLI_FACE_ID
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/test-env')
def test_env():
    """Test endpoint to verify environment variables are loaded."""
    return jsonify({
        "simli_api_key_set": bool(SIMLI_API_KEY and SIMLI_API_KEY != "your_simli_api_key_here"),
        "simli_agent_id_set": bool(SIMLI_AGENT_ID),
        "simli_face_id_set": bool(SIMLI_FACE_ID and SIMLI_FACE_ID != "your_simli_face_id_here"),
        "livekit_url": LIVEKIT_URL[:30] + "..." if LIVEKIT_URL and len(LIVEKIT_URL) > 30 else LIVEKIT_URL,
        "livekit_url_format_ok": LIVEKIT_URL.startswith("wss://") if LIVEKIT_URL else False,
        "livekit_api_key_set": bool(LIVEKIT_API_KEY),
        "livekit_api_secret_set": bool(LIVEKIT_API_SECRET),
        "openai_key_set": bool(OPENAI_API_KEY),
        "elevenlabs_key_set": bool(ELEVENLABS_API_KEY),
        "livekit_sdk_loaded": livekit_api is not None,
    })


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


@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    Streams GPT-4o response sentence by sentence for synchronized text + voice.
    """
    data = request.json
    user_message = data.get('message', '')
    visible_context = data.get('context', '')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Check for doodle (no streaming for doodles)
    doodle = check_for_doodle(user_message)
    if doodle:
        return jsonify({"doodle": doodle})

    if not openai_client:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    # Build messages for the API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if visible_context:
        context_msg = f"""
The reader is currently looking at this passage:

---
{visible_context[:2000]}
---

Keep this context in mind when responding. You can reference it naturally without the user having to point it out.
"""
        messages.append({"role": "system", "content": context_msg})

    for msg in chat_history[-12:]:
        role = "user" if msg.get("type") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": user_message})

    def generate():
        """Generator that yields SSE events with sentences."""
        try:
            # Stream from OpenAI
            stream = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=600,
                temperature=0.8,
                stream=True
            )

            buffer = ""
            sentence_endings = re.compile(r'([.!?])\s+')

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    buffer += chunk.choices[0].delta.content

                    # Check for complete sentences
                    while True:
                        match = sentence_endings.search(buffer)
                        if match:
                            # Extract the sentence (including the punctuation)
                            end_pos = match.end()
                            sentence = buffer[:end_pos].strip()
                            buffer = buffer[end_pos:]

                            if sentence:
                                # Send the sentence as an SSE event
                                event_data = json.dumps({"sentence": sentence})
                                yield f"data: {event_data}\n\n"
                        else:
                            break

            # Send any remaining text
            if buffer.strip():
                event_data = json.dumps({"sentence": buffer.strip()})
                yield f"data: {event_data}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using ElevenLabs.
    Returns base64-encoded audio.
    """
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        return jsonify({"error": "ElevenLabs not configured"}), 500

    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
            headers={
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            },
            json={
                "text": text,
                "model_id": "eleven_turbo_v2",  # Faster model for lower latency
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            # Return base64-encoded audio
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return jsonify({
                "audio": audio_base64,
                "content_type": "audio/mpeg"
            })
        else:
            return jsonify({"error": f"ElevenLabs error: {response.status_code}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
