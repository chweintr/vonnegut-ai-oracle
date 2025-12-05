# -*- coding: utf-8 -*-
"""
Vonnebot: A Kurt Vonnegut Inspired Reading Companion
Clean, minimal implementation with:
- Left: Reading pane (scrollable, tracks visible content)
- Right top: Simli avatar (circular)
- Right bottom: Chat thread (scrollable)
"""

import streamlit as st
import streamlit.components.v1 as components
import openai
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
SIMLI_FACE_ID = os.getenv("SIMLI_FACE_ID")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Load Vonnegut system prompt
PROMPT_PATH = Path("prompts_base_prompt.txt")
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "You are Kurt Vonnegut."

# Sample texts for the reading pane
SAMPLE_TEXTS = {
    "2BR02B (1962)": Path("data/vonnegut_corpus/public_domain/2BR02B.txt"),
    "Harrison Bergeron": Path("data/vonnegut_corpus/public_domain/HarrisonBergeron.txt"),
    "The Big Trip Up Yonder": Path("data/vonnegut_corpus/public_domain/TheBigTripUpYonder.txt"),
}


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_visible_context(full_text: str, scroll_position: int = 0, window_size: int = 2000) -> str:
    """Extract the portion of text that would be 'visible' based on scroll position."""
    start = max(0, scroll_position)
    end = start + window_size
    return full_text[start:end]


def generate_response(user_message: str, visible_context: str, chat_history: list) -> str:
    """Generate a response from Vonnebot with awareness of what user is reading."""
    if not openai_client:
        return "OpenAI API key not configured. Please add OPENAI_API_KEY to environment variables."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add context about what user is currently reading
    if visible_context:
        context_msg = f"""
The reader is currently looking at this passage:

---
{visible_context[:1500]}
---

Keep this context in mind when responding. You can reference it naturally without the user having to point it out.
"""
        messages.append({"role": "system", "content": context_msg})

    # Add chat history (last 6 messages)
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=600,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I seem to be having trouble. So it goes. Error: {str(e)}"


def render_avatar():
    """Render the Simli avatar or placeholder."""
    if LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
        # TODO: Implement LiveKit connection when agent backend is ready
        st.markdown(
            """
            <div style="width: 200px; height: 200px; border-radius: 50%; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 2px solid #f9c46b;">
                <span style="color: #f9c46b; font-size: 14px; text-align: center;">Voice mode<br/>coming soon</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="width: 200px; height: 200px; border-radius: 50%; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 2px solid #333;">
                <span style="color: #666; font-size: 12px; text-align: center;">Avatar<br/>not configured</span>
            </div>
            """,
            unsafe_allow_html=True
        )


# -----------------------------------------------------------------------------
# Main App
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Vonnebot",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for dark theme and layout
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg-dark: #0a0a0f;
        --bg-card: #12121a;
        --bg-input: #1a1a24;
        --accent: #f9c46b;
        --text: #e8e8e8;
        --text-muted: #888;
        --border: #2a2a35;
    }

    .stApp {
        background: var(--bg-dark);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}

    /* Main container */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
    }

    /* Header */
    .vonnebot-header {
        text-align: center;
        padding: 1rem 0 1.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }

    .vonnebot-header h1 {
        font-size: 2rem;
        margin: 0;
        color: var(--accent);
    }

    .vonnebot-header p {
        color: var(--text-muted);
        margin: 0.5rem 0 0;
        font-size: 0.9rem;
    }

    /* Reading pane */
    .reading-pane {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        height: 70vh;
        overflow-y: auto;
        line-height: 1.7;
        font-size: 1rem;
    }

    .reading-pane::-webkit-scrollbar {
        width: 8px;
    }

    .reading-pane::-webkit-scrollbar-thumb {
        background: var(--accent);
        border-radius: 4px;
    }

    /* Chat container */
    .chat-container {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        height: 45vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }

    .chat-container::-webkit-scrollbar {
        width: 6px;
    }

    .chat-container::-webkit-scrollbar-thumb {
        background: #444;
        border-radius: 3px;
    }

    /* Chat messages */
    .chat-message {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        max-width: 90%;
    }

    .chat-message.user {
        background: var(--bg-input);
        margin-left: auto;
        border: 1px solid var(--border);
    }

    .chat-message.assistant {
        background: rgba(249, 196, 107, 0.1);
        border: 1px solid rgba(249, 196, 107, 0.3);
        margin-right: auto;
    }

    .chat-message .role {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: 0.25rem;
    }

    .chat-message.assistant .role {
        color: var(--accent);
    }

    /* Input area */
    .stTextInput input {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        padding: 0.75rem !important;
    }

    .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    .stButton button {
        background: var(--accent) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* Disclaimer */
    .disclaimer {
        text-align: center;
        padding: 1rem;
        color: var(--text-muted);
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
        margin-top: 1rem;
    }

    .disclaimer a {
        color: var(--accent);
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="vonnebot-header">
        <h1>Vonnebot</h1>
        <p>A Kurt Vonnegut Inspired Reading Companion</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_text" not in st.session_state:
        st.session_state.current_text = ""
    if "visible_context" not in st.session_state:
        st.session_state.visible_context = ""

    # Two-column layout
    col_left, col_right = st.columns([1, 1], gap="medium")

    # LEFT COLUMN: Reading Pane
    with col_left:
        st.markdown("#### 📖 Reading Pane")

        # Text source selector
        source_option = st.selectbox(
            "Choose a text:",
            ["-- Select --", "Upload your own"] + list(SAMPLE_TEXTS.keys()),
            label_visibility="collapsed"
        )

        # Handle text loading
        if source_option == "Upload your own":
            uploaded = st.file_uploader("Upload .txt file", type=["txt"], label_visibility="collapsed")
            if uploaded:
                st.session_state.current_text = uploaded.read().decode("utf-8")
        elif source_option != "-- Select --":
            path = SAMPLE_TEXTS.get(source_option)
            if path and path.exists():
                st.session_state.current_text = path.read_text(encoding="utf-8")

        # Display reading pane
        if st.session_state.current_text:
            # Store visible context (first ~2000 chars for now, could be smarter with JS)
            st.session_state.visible_context = st.session_state.current_text[:2000]

            st.markdown(
                f'<div class="reading-pane">{st.session_state.current_text.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="reading-pane" style="display: flex; align-items: center; justify-content: center; color: var(--text-muted);">
                    <p>Select a text above or upload your own to begin reading.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # RIGHT COLUMN: Avatar + Chat
    with col_right:
        # Avatar section
        st.markdown("#### 🎭 Vonnebot")
        render_avatar()

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        # Chat section
        st.markdown("#### 💬 Chat")

        # Chat history display
        chat_html = '<div class="chat-container">'
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                role_class = msg["role"]
                role_label = "You" if msg["role"] == "user" else "Kurt"
                chat_html += f'''
                <div class="chat-message {role_class}">
                    <div class="role">{role_label}</div>
                    <div>{msg["content"]}</div>
                </div>
                '''
        else:
            chat_html += '<p style="color: var(--text-muted); text-align: center; margin: auto;">Ask me anything about what you\'re reading.</p>'
        chat_html += '</div>'

        st.markdown(chat_html, unsafe_allow_html=True)

        # Input area
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Message",
                placeholder="Ask about the passage, themes, or anything else...",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Send")

        if submitted and user_input.strip():
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Generate response with visible context
            with st.spinner("Kurt is thinking..."):
                response = generate_response(
                    user_input,
                    st.session_state.visible_context,
                    st.session_state.chat_history
                )

            # Add assistant message
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        # Clear chat button
        if st.session_state.chat_history:
            if st.button("Clear chat", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <details>
            <summary style="cursor: pointer; color: #f9c46b;">About Vonnebot</summary>
            <p style="margin-top: 0.5rem;">
                Vonnebot is an AI tool trained on Kurt Vonnegut's writings to offer readers additional context and insights.
                It's a way to engage with his work interactively—not a literal channeling of Vonnegut himself.
                Born in 1922, he had his own views on technology; while we think he might have found this intriguing,
                we acknowledge this is just an approximation. This project is not affiliated with or endorsed by the Vonnegut estate.
            </p>
        </details>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
