# -*- coding: utf-8 -*-
"""
Vonnebot: A Kurt Vonnegut Inspired Reading Companion
Flask backend with beautiful typewriter-style frontend
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import openai
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Simli configuration
SIMLI_AGENT_ID = os.getenv("SIMLI_AGENT_ID")

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


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route('/')
def index():
    """Serve the main page."""
    return render_template(
        'index.html',
        texts=list(AVAILABLE_TEXTS.keys()),
        simli_agent_id=SIMLI_AGENT_ID
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


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.json
    user_message = data.get('message', '')
    visible_context = data.get('context', '')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

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
