# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import openai
import requests
import base64
import os
from dotenv import load_dotenv
import time
from pathlib import Path
from html import escape

import knowledge_base

EXCERPT_SOURCES = {
    "Slaughterhouse-Five (Excerpt)": Path("data/excerpts/slaughterhouse_five_excerpt.txt"),
    "Cat's Cradle (Excerpt)": Path("data/excerpts/cats_cradle_excerpt.txt"),
    "Breakfast of Champions (Excerpt)": Path("data/excerpts/breakfast_of_champions_excerpt.txt"),
}

PROFILE_CATEGORIES = [
    "General Reader",
    "High School Student",
    "Undergraduate",
    "Graduate / Scholar",
    "Creative Writer",
    "Educator",
]

DISCIPLINE_OPTIONS = [
    "Undeclared / Exploring",
    "Humanities",
    "Social Sciences",
    "STEM",
    "Business",
    "Fine Arts",
    "Education",
    "Other",
]

READING_EXPERIENCE_OPTIONS = [
    "New to Vonnegut",
    "Read 1-2 works",
    "Familiar with several novels",
    "Dedicated scholar",
]

# LiveKit Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Simli Configuration (still needed for agent backend)
SIMLI_API_KEY = os.getenv("SIMLI_API_KEY")
SIMLI_FACE_ID = os.getenv("SIMLI_FACE_ID")
SIMLI_AGENT_ID = os.getenv("SIMLI_AGENT_ID")


def generate_livekit_token(room_name: str = "vonnebot-room", participant_name: str = None) -> str:
    """Generate a LiveKit access token for the frontend."""
    try:
        from livekit import api
    except ImportError:
        st.warning("LiveKit SDK not available")
        return None

    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return None

    if not participant_name:
        participant_name = f"user-{int(time.time())}"

    try:
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        token.with_ttl(3600)
        return token.to_jwt()
    except Exception as e:
        st.warning(f"Token generation failed: {e}")
        return None


def render_simli_avatar():
    """Render Simli avatar via LiveKit connection, with fallback to placeholder."""
    # Check if LiveKit is configured
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        # Fallback: show placeholder with message
        st.markdown(
            """
            <div style="width: 100%; height: 520px; background-color: #111; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 1px solid #333; border-radius: 8px;">
                <p style="color: #888; font-size: 16px;">Voice avatar not configured</p>
                <p style="color: #666; font-size: 12px;">Use text mode below to chat with Vonnebot</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Generate token for this session
    room_name = "vonnebot-room"
    token = generate_livekit_token(room_name)

    if not token:
        st.markdown(
            """
            <div style="width: 100%; height: 520px; background-color: #111; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 1px solid #333; border-radius: 8px;">
                <p style="color: #f5a623; font-size: 16px;">Could not connect to voice service</p>
                <p style="color: #666; font-size: 12px;">Use text mode below to chat with Vonnebot</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # LiveKit Meet embed with token
    livekit_html = f"""
    <div id="vonnebot-avatar" style="width: 100%; height: 520px; border-radius: 8px; overflow: hidden; background-color: #000;">
        <iframe
            src="https://meet.livekit.io/custom?liveKitUrl={LIVEKIT_URL}&token={token}"
            width="100%"
            height="100%"
            frameborder="0"
            allow="microphone; camera; autoplay"
            style="border: none;"
        ></iframe>
    </div>
    """
    components.html(livekit_html, height=520, scrolling=False)


LEARNING_FOCUS_OPTIONS = [
    "Historical context",
    "Close textual analysis",
    "Biographical connections",
    "Writing craft",
    "Philosophical themes",
    "Classroom application",
]

RESPONSE_DEPTH_OPTIONS = ["Concise", "Balanced", "In-depth"]

BASE_PROMPT_PATH = Path("prompts_base_prompt.txt")
EDUCATIONAL_MODE_PROMPT = Path("prompts/educational_mode.txt").read_text(encoding="utf-8")
PASSAGE_CONTEXT_PROMPT = Path("prompts/passage_context_template.txt").read_text(encoding="utf-8")

def get_video_base64():
    """Encode video file as base64 for embedding"""
    try:
        with open("vonnegut_blinking.mp4", "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode()
            return video_base64
    except FileNotFoundError:
        return ""

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
CORPUS_EMBEDDING_MODEL = os.getenv("CORPUS_EMBEDDING_MODEL", "text-embedding-3-large")

def get_vonnegut_system_prompt(educational_mode=False, passage_context=None):
    """Generate comprehensive system prompt with optional educational enhancement"""

    base_prompt = BASE_PROMPT_PATH.read_text(encoding="utf-8")



    # Add educational enhancement if in learning guide mode
    if educational_mode:
        base_prompt += EDUCATIONAL_MODE_PROMPT



    # Add passage context if provided
    if passage_context:
        base_prompt += PASSAGE_CONTEXT_PROMPT.replace("__PASSAGE__", passage_context)



    return base_prompt


def init_user_profile_state():
    default_profile = {
        "reader_category": PROFILE_CATEGORIES[0],
        "region": "",
        "discipline": DISCIPLINE_OPTIONS[0],
        "reading_experience": READING_EXPERIENCE_OPTIONS[0],
        "learning_focus": [LEARNING_FOCUS_OPTIONS[1]],
        "response_depth": "Balanced",
        "language_pref": "English",
        "purpose": "General curiosity",
    }

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = default_profile
        return

    for key, value in default_profile.items():
        st.session_state.user_profile.setdefault(key, value)


def render_profile_settings(container=None, key_prefix="profile_"):

    init_user_profile_state()

    target = container or st.sidebar
    profile = st.session_state.user_profile

    profile_panel = target.expander(
        "Reader profile", expanded=not st.session_state.get("profile_acknowledged", False)
    )

    with profile_panel:
        profile["reader_category"] = profile_panel.selectbox(
            "Who are you reading as today?",
            PROFILE_CATEGORIES,
            index=PROFILE_CATEGORIES.index(profile.get("reader_category", PROFILE_CATEGORIES[0])),
            key=f"{key_prefix}reader_category",
        )

        profile["discipline"] = profile_panel.selectbox(
            "Field or lens",
            DISCIPLINE_OPTIONS,
            index=DISCIPLINE_OPTIONS.index(profile.get("discipline", DISCIPLINE_OPTIONS[0])),
            key=f"{key_prefix}discipline",
        )

        profile["region"] = profile_panel.text_input(
            "Where are you based? (City / Region)",
            value=profile.get("region", ""),
            key=f"{key_prefix}region",
        )

        profile["reading_experience"] = profile_panel.selectbox(
            "Vonnegut experience",
            READING_EXPERIENCE_OPTIONS,
            index=READING_EXPERIENCE_OPTIONS.index(
                profile.get("reading_experience", READING_EXPERIENCE_OPTIONS[0])
            ),
            key=f"{key_prefix}experience",
        )

        profile["learning_focus"] = profile_panel.multiselect(
            "What should Kurt emphasize?",
            LEARNING_FOCUS_OPTIONS,
            default=profile.get("learning_focus", [LEARNING_FOCUS_OPTIONS[1]]),
            key=f"{key_prefix}focus",
        )

        profile["response_depth"] = profile_panel.radio(
            "Response depth",
            RESPONSE_DEPTH_OPTIONS,
            index=RESPONSE_DEPTH_OPTIONS.index(profile.get("response_depth", "Balanced")),
            key=f"{key_prefix}depth",
            horizontal=True,
        )

        profile["language_pref"] = profile_panel.text_input(
            "Primary language or dialect",
            value=profile.get("language_pref", "English"),
            key=f"{key_prefix}language",
        )

        profile["purpose"] = profile_panel.text_input(
            "Why are you reading today?",
            value=profile.get("purpose", "General curiosity"),
            key=f"{key_prefix}purpose",
        )

        st.session_state.profile_acknowledged = True


def build_profile_context():
    profile = st.session_state.get("user_profile")
    if not profile:
        return None

    focus = profile.get("learning_focus") or []
    focus_text = ", ".join(focus) if focus else "general insights"

    lines = [
        "Reader profile for this session:",
        f"- Category: {profile.get('reader_category')}",
        f"- Region / dialect cues: {profile.get('region') or 'unspecified'}",
        f"- Discipline or lens: {profile.get('discipline')}",
        f"- Vonnegut familiarity: {profile.get('reading_experience')}",
        f"- Preferred focus: {focus_text}",
        f"- Desired response depth: {profile.get('response_depth', 'Balanced')}",
        f"- Primary language: {profile.get('language_pref', 'English')}",
        f"- Session purpose: {profile.get('purpose', 'General curiosity')}",
        "Tailor tone, analogies, and cultural references to this profile."
    ]

    return "\n".join(lines)

def generate_vonnegut_response(user_input, conversation_history, educational_mode=False, passage_context=None):
    """Generate response using OpenAI with Vonnegut personality"""

    system_prompt = get_vonnegut_system_prompt(educational_mode, passage_context)

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    profile_context = build_profile_context()
    if profile_context:
        messages.append({"role": "system", "content": profile_context})

    # Add conversation history
    for msg in conversation_history[-6:]:  # Keep last 6 messages for context
        messages.append(msg)

    reference_context = build_reference_context(user_input, passage_context)
    if reference_context:
        messages.append({"role": "system", "content": reference_context})

    messages.append({"role": "user", "content": user_input})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Listen: I seem to be having trouble connecting to my thoughts right now. So it goes. Error: {str(e)}"

def synthesize_speech(text):
    """Convert text to speech using ElevenLabs API"""
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        st.error("🚫 Missing ElevenLabs credentials")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"❌ ElevenLabs API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"💥 Error calling ElevenLabs: {str(e)}")
        return None

def load_text_library():
    """Load available texts from data directory and private excerpts."""
    texts = {}
    missing_excerpts = []
    data_dir = Path("data/raw")

    if data_dir.exists():
        # Load the two public domain stories
        pg_2br02b = data_dir / "pg_2br02b.txt"
        pg_big_trip = data_dir / "pg_big_trip_up_yonder.txt"

        if pg_2br02b.exists():
            with open(pg_2br02b, 'r', encoding='utf-8') as f:
                texts["2BR02B (1962)"] = f.read()

        if pg_big_trip.exists():
            with open(pg_big_trip, 'r', encoding='utf-8') as f:
                texts["The Big Trip Up Yonder (1954)"] = f.read()

    for label, path in EXCERPT_SOURCES.items():
        if not path.exists():
            missing_excerpts.append(label)
            continue

        with open(path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        cleaned_lines = [
            line
            for line in raw_text.splitlines()
            if not line.strip().startswith('#')
        ]
        excerpt_text = "\n".join(cleaned_lines).strip()

        if excerpt_text:
            texts[label] = excerpt_text
        else:
            missing_excerpts.append(label)

    return texts, missing_excerpts


QUICK_ACTION_PROMPTS = {
    "ask": "Can you walk me through what stands out in this passage?",
    "themes": "What themes or motifs are present in this passage?",
    "explain": "Can you explain this passage and its significance?"
}




def display_reading_text(text_content, component_key="reading_pane"):
    """Pure Streamlit reading pane with paragraph quick-select fallback."""

    if not text_content:
        return None

    safe_key = component_key or "reading_pane"

    st.markdown(
        f"""
        <div class='reading-pane-wrapper'>
            <div class='interactive-reading'>{format_text_for_display(text_content)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    paragraphs = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
    selection_payload = None

    if paragraphs:
        options = list(range(len(paragraphs)))

        def _format(idx: int) -> str:
            snippet = paragraphs[idx].replace("\n", " ")
            if len(snippet) > 140:
                snippet = snippet[:140].rsplit(" ", 1)[0] + "…"
            return f"Paragraph {idx + 1}: {snippet}"

        selected_idx = st.selectbox(
            "Quick-select a paragraph",
            options,
            format_func=_format,
            key=f"paragraph_selector_{safe_key}"
        )

        if st.button("Ask about this paragraph", key=f"use_paragraph_{safe_key}"):
            selection_payload = {"action": "ask", "text": paragraphs[selected_idx]}

    manual_passage = st.text_area(
        "Or paste/type your own passage",
        value=st.session_state.get("selected_passage", ""),
        key=f"manual_passage_{safe_key}"
    )

    if st.button("Use manual passage", key=f"use_manual_{safe_key}"):
        cleaned = manual_passage.strip()
        if cleaned:
            selection_payload = {"action": "ask", "text": cleaned}

    return selection_payload




def fetch_reference_snippets(query_text, top_k=3):
    if not knowledge_base.index_available():
        return []

    try:
        embedding = openai_client.embeddings.create(
            model=CORPUS_EMBEDDING_MODEL,
            input=[query_text]
        ).data[0].embedding
    except Exception as exc:
        # Surface failure once per rerun via Streamlit, but avoid breaking chats
        st.warning(f"Corpus retrieval unavailable: {exc}")
        return []

    return knowledge_base.search_by_embedding(embedding, top_k=top_k)


def build_reference_context(user_input, passage_context=None, max_snippets=3):
    query_text = user_input or ""
    if passage_context:
        query_text = f"{user_input}\n\nPassage of focus:\n{passage_context}"

    snippets = fetch_reference_snippets(query_text, top_k=max_snippets)
    if not snippets:
        return None

    formatted_snippets = []
    for snippet in snippets:
        text = snippet["text"].strip()
        if len(text) > 600:
            text = text[:600].rsplit(" ", 1)[0] + "..."
        formatted = f"Source: {snippet['source']}\nExcerpt: {text}"
        formatted_snippets.append(formatted)

    joined = "\n\n".join(formatted_snippets)
    return (
        "Reference these authentic Vonnegut materials when you respond. "
        "Focus on consistency with the cited excerpts.\n\n" + joined
    )


def submit_learning_question(question, passage=None, voice_enabled=False):
    """Persist user question, call OpenAI, append response, and optionally voice"""

    cleaned_question = (question or "").strip()
    if not cleaned_question:
        return None

    passage_text = passage or st.session_state.get("selected_passage")
    model_content = cleaned_question

    if passage_text:
        model_content = f"Regarding this passage:\n\n\"{passage_text}\"\n\n{cleaned_question}"

    st.session_state.learning_history.append({
        "role": "user",
        "content": cleaned_question,
        "passage": passage_text,
        "model_content": model_content
    })

    sanitized_history = [
        {
            "role": msg["role"],
            "content": msg.get("model_content", msg["content"])
        }
        for msg in st.session_state.learning_history[:-1]
        if msg.get("role") in ("user", "assistant")
    ]

    with st.spinner("Kurt is thinking..."):
        response = generate_vonnegut_response(
            model_content,
            sanitized_history,
            educational_mode=True,
            passage_context=passage_text
        )

    st.session_state.learning_history.append({
        "role": "assistant",
        "content": response
    })

    if voice_enabled and ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
        with st.spinner("Generating voice..."):
            audio_data = synthesize_speech(response)
            if audio_data:
                st.audio(audio_data, format="audio/mpeg")

    return response


def format_text_for_display(text):
    """Escape HTML characters and preserve line breaks"""
    return escape(text).replace("\n", "<br>")

def chat_interface():
    """Original chat interface"""
    st.markdown(
        '<p class="vlg-section-subtitle">Classic conversation mode. Ask anything and keep Kurt grounded in authentic texts.</p>',
        unsafe_allow_html=True
    )

    # Display conversation history
    for msg in st.session_state.conversation_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message vonnegut-message">
                <strong>Kurt Vonnegut:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)

    # Conversation mode selector
    col_mode1, col_mode2 = st.columns([2, 3])

    with col_mode1:
        conversation_mode = st.selectbox(
            "Conversation mode:",
            options=["Text → Text", "Text → Audio", "Audio → Audio"],
            index=1 if (ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID) else 0,
            key="chat_mode"
        )

    with col_mode2:
        if conversation_mode == "Audio → Audio":
            st.caption("🎤 Click to speak → Kurt responds with voice")
        elif conversation_mode == "Text → Audio":
            st.caption("⌨️ Type your message → Kurt responds with voice")
        else:
            st.caption("⌨️ Type your message → Kurt responds with text")

    # User input based on mode
    user_input = ""
    send_button = False

    if conversation_mode == "Audio → Audio":
        st.markdown("### 🎤 Voice Conversation with Kurt")

        try:
            from streamlit_mic_recorder import speech_to_text

            st.info("🎤 **Speak to Kurt - he'll respond with voice automatically!**")

            speech_text = speech_to_text(
                language='en',
                start_prompt="🎤 Click and Speak to Kurt",
                stop_prompt="⏹️ Stop recording",
                just_once=False,
                key="kurt_conversation_chat"
            )

            if speech_text:
                st.success(f"🎤 You said: \"{speech_text}\" → Sending to Kurt...")
                user_input = speech_text
                send_button = True
            else:
                user_input = ""
                send_button = False

        except ImportError:
            st.error("⚠️ streamlit-mic-recorder not installed yet...")
            st.info("Installing... please refresh in 1-2 minutes")
            user_input = ""
            send_button = False
        except Exception as e:
            st.error(f"Error with mic recorder: {str(e)}")
            user_input = ""
            send_button = False

    else:
        user_input = st.text_input("Ask Kurt anything:", placeholder="What did you learn from your Dresden experience?", key="chat_input")

        col1, col2 = st.columns([1, 4])

        with col1:
            send_button = st.button("Send", type="primary", key="chat_send")

        with col2:
            st.caption("💭 Kurt will respond in your selected mode")

    if send_button and user_input:
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        with st.spinner("Kurt is thinking..."):
            response = generate_vonnegut_response(
                user_input,
                st.session_state.conversation_history,
                educational_mode=False
            )

        st.session_state.conversation_history.append({"role": "assistant", "content": response})

        voice_output_enabled = (conversation_mode in ["Text → Audio", "Audio → Audio"]) and ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID

        if voice_output_enabled:
            with st.spinner("*"):
                audio_data = synthesize_speech(response)
                if audio_data:
                    st.audio(audio_data, format="audio/mpeg", start_time=0)
                else:
                    st.error("❌ Voice generation failed - no audio data")

        if not voice_output_enabled:
            st.rerun()

def learning_guide_interface():
    """Lean learning guide interface with highlight-to-ask workflow"""
    text_library, missing_excerpts = load_text_library()
    selection_event = None

    # Layout: 2 Columns
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📄 Import Text")
        st.markdown("<div class='upload-hint'>Upload a .txt file to analyze.</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload a text file", type=['txt'], key="reading_upload", label_visibility="collapsed")

        st.markdown(
            """
            <div class="vlg-section">
                <h2 class="vlg-section-title">Reading pane</h2>
                <p class="vlg-section-subtitle">Highlight any sentence or paragraph, then choose Ask Kurt or explore themes.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not knowledge_base.index_available():
            st.markdown(
                """
                <div class="vlg-alert">
                    <div>
                        <h3>Corpus index missing</h3>
                        <p>The knowledge base index is not found. Please rebuild it to enable citations.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Rebuild Corpus Index", key="rebuild_corpus_btn"):
                with st.spinner("Rebuilding corpus index..."):
                    try:
                        # Run the build script logic directly or via subprocess
                        import subprocess
                        result = subprocess.run(["python", "build_corpus_index.py"], capture_output=True, text=True)
                        if result.returncode == 0:
                            st.success("Corpus index built successfully! Please refresh the page.")
                            knowledge_base.clear_cache()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Failed to build index: {result.stderr}")
                    except Exception as e:
                        st.error(f"Error rebuilding index: {str(e)}")

        text_options = ["-- Select a text --"] + list(text_library.keys()) if text_library else ["-- No texts available --"]
        selected_text_name = st.selectbox(
            "Library texts",
            options=text_options,
            index=0,
            key="text_selector"
        )

        text_content = None
        component_key = "library"

        if text_library and selected_text_name != "-- Select a text --":
            text_content = text_library[selected_text_name]
            component_key = selected_text_name.replace(" ", "_").lower()

        if uploaded_file:
            text_content = uploaded_file.read().decode('utf-8')
            component_key = f"upload_{uploaded_file.name.replace(' ', '_').lower()}"

        if text_content:
            selection_event = display_reading_text(text_content, component_key=component_key)
            st.caption("Tip: Select a paragraph above or paste your own passage.")
        else:
            st.markdown(
                """
                <div class="empty-state-card">
                    Load a library text or upload your own .txt file to begin.
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_right:
        # Simli Avatar Container
        st.markdown("#### 🤖 Vonnebot")
        
        # Render Simli based on mode
        if st.session_state.interaction_mode == "Talk":
            render_simli_avatar()
        else:
            # Idle State - Static Image or Video Loop
            st.markdown(
                """
                <div style="width: 100%; height: 520px; background-color: #111; display: flex; justify-content: center; align-items: center; border: 1px solid #333; border-radius: 8px; overflow: hidden;">
                    <div style="text-align: center; color: #666;">
                        <p style="font-size: 48px; margin-bottom: 10px;">😴</p>
                        <p>Vonnebot is listening via Text</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Mode Toggle Buttons
        st.write("") # Spacer
        mode_cols = st.columns(2)
        with mode_cols[0]:
            if st.button("📝 Text Mode", use_container_width=True, type="primary" if st.session_state.interaction_mode == "Text" else "secondary"):
                st.session_state.interaction_mode = "Text"
                st.rerun()
        with mode_cols[1]:
            if st.button("🗣️ Talk Mode", use_container_width=True, type="primary" if st.session_state.interaction_mode == "Talk" else "secondary"):
                st.session_state.interaction_mode = "Talk"
                st.rerun()

        st.markdown("---")
        st.markdown("#### 💬 Conversation")

        selected_passage = st.session_state.get("selected_passage")
        voice_enabled = st.session_state.get("guide_voice", False)

        if selection_event and isinstance(selection_event, dict):
            highlighted_text = (selection_event.get("text") or "").strip()
            action = selection_event.get("action", "ask")
            if highlighted_text:
                st.session_state.selected_passage = highlighted_text
                question_prompt = QUICK_ACTION_PROMPTS.get(action, QUICK_ACTION_PROMPTS["ask"])
                submit_learning_question(
                    question_prompt,
                    passage=highlighted_text,
                    voice_enabled=voice_enabled
                )
                st.rerun()

        selected_passage = st.session_state.get("selected_passage")

        if selected_passage:
            st.markdown(
                f"""
                <div class="selected-passage-card">
                    <div class="selected-label">Selected passage</div>
                    <p>{format_text_for_display(selected_passage)}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Reset", key="clear_selection"):
                st.session_state.selected_passage = None
                st.session_state.learning_history = []
                st.rerun()
        else:
            st.markdown(
                """
                <div class="empty-state-card">
                    Select a passage on the left to start a conversation.
                </div>
                """,
                unsafe_allow_html=True
            )

        conversation = st.session_state.learning_history[-8:]

        if conversation:
            for msg in conversation:
                if msg["role"] == "user":
                    card = f"""
                    <div class="guide-message user-message">
                        <strong>You:</strong> {format_text_for_display(msg['content'])}
                    </div>
                    """
                else:
                    card = f"""
                    <div class="guide-message vonnegut-message">
                        <strong>Kurt:</strong> {msg['content']}<br>
                        <small class="sim-note"><em>*Educational simulation*</em></small>
                    </div>
                    """
                st.markdown(card, unsafe_allow_html=True)

        quick_cols = st.columns(2)
        with quick_cols[0]:
            if st.button("Explain this", key="explain_btn", disabled=not selected_passage):
                submit_learning_question(
                    QUICK_ACTION_PROMPTS["explain"],
                    passage=selected_passage,
                    voice_enabled=voice_enabled
                )
                st.rerun()

        with quick_cols[1]:
            if st.button("Themes", key="themes_btn", disabled=not selected_passage):
                submit_learning_question(
                    QUICK_ACTION_PROMPTS["themes"],
                    passage=selected_passage,
                    voice_enabled=voice_enabled
                )
                st.rerun()

        # General Chat Input
        user_question = st.text_input(
            "Ask Vonnebot...",
            placeholder="Type your question here...",
            key="guide_user_question"
        )
        
        cols_actions = st.columns([2, 1])
        with cols_actions[0]:
            if st.button("Send", key="guide_send"):
                if user_question.strip():
                    submit_learning_question(
                        user_question,
                        passage=selected_passage, # Will be None if not selected, or the text if selected
                        voice_enabled=voice_enabled
                    )
                    st.session_state.guide_user_question = "" # Clear input
                    st.rerun()
                else:
                    st.warning("Please enter a question.")

        with cols_actions[1]:
            voice_enabled = st.checkbox("🔊 Voice", value=voice_enabled, key="guide_voice")

        if st.button("Clear conversation", key="clear_learning_history", disabled=not conversation):
            st.session_state.learning_history = []
            st.rerun()

def main():
    # Set page config
    st.set_page_config(
        page_title="Vonnebot: A Kurt Vonnegut Inspired Reading Companion",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    /* Video Background */
    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        object-fit: cover;
        opacity: 0.3;
        filter: sepia(60%) hue-rotate(20deg) saturate(0.7) brightness(1.1) contrast(0.7);
        pointer-events: none;
    }

    :root {
        --vlg-bg: #050608;
        --vlg-bg-elevated: #151820;
        --vlg-bg-soft: #1d212b;
        --vlg-border-subtle: #272b36;
        --vlg-accent: #f9c46b;
        --vlg-accent-strong: #ff6b35;
        --vlg-text: #f5f5f5;
        --vlg-text-muted: #a1a6b4;
        --vlg-link: #4fd0ff;
        --vlg-danger: #f5a623;
        --vlg-radius-lg: 18px;
        --vlg-radius-xl: 24px;
        --vlg-shadow-soft: 0 18px 40px rgba(0, 0, 0, 0.6);
        --vlg-transition-fast: 150ms ease-out;
    }

    body, .stApp {
        margin: 0;
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        background: radial-gradient(circle at top, #1b1d26 0, #050608 55%) fixed;
        color: var(--vlg-text);
    }

    .stApp {
        min-height: 100vh;
    }

    .main .block-container {
        max-width: 1040px;
        padding-top: 12px;
        padding-bottom: 160px;
    }

    .stMain, .main .block-container {
        background: transparent;
    }

    .stSidebar {
        background: linear-gradient(180deg, rgba(9, 10, 15, 0.95), rgba(6, 7, 9, 0.92));
    }

    .stSidebar, .stSidebar * {
        color: var(--vlg-text) !important;
    }

    .stSidebar .stButton>button {
        width: 100%;
    }

    .vlg-root {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .vlg-header {
        padding: 32px 0 8px;
    }

    .vlg-header-inner {
        max-width: 1040px;
        margin: 0 auto;
    }

    .vlg-title {
        margin: 0 0 8px;
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 46px;
        letter-spacing: 0.04em;
    }

    .vlg-quote {
        margin: 0 0 4px;
        font-style: italic;
        color: var(--vlg-text-muted);
    }

    .vlg-tagline {
        margin: 0 0 20px;
        padding: 8px 14px;
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        background: rgba(10, 10, 10, 0.7);
        border: 1px solid rgba(249, 196, 107, 0.4);
        color: var(--vlg-text-muted);
        font-size: 13px;
    }

    .vlg-description {
        max-width: 640px;
        color: rgba(245, 245, 245, 0.9);
        margin: 0;
    }

    .vlg-main {
        flex: 1;
    }

    .vlg-card {
        background: linear-gradient(135deg, rgba(21, 24, 32, 0.96), rgba(9, 10, 16, 0.96));
        border-radius: var(--vlg-radius-xl);
        padding: 28px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        box-shadow: var(--vlg-shadow-soft);
        margin-bottom: 24px;
    }

    .vlg-alert {
        display: flex;
        gap: 14px;
        padding: 14px 16px;
        border-radius: 14px;
        margin-bottom: 20px;
        border: 1px solid rgba(245, 166, 35, 0.4);
        background: radial-gradient(circle at top left, rgba(245, 166, 35, 0.25), transparent 65%),
            rgba(30, 24, 8, 0.9);
    }

    .vlg-alert h3 {
        margin: 0 0 4px;
        font-size: 16px;
    }

    .vlg-alert p {
        margin: 0;
        font-size: 13px;
        color: #fbdcaa;
    }

    .vlg-info {
        display: flex;
        gap: 12px;
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(20, 32, 52, 0.95);
        border: 1px solid rgba(79, 208, 255, 0.45);
        font-size: 13px;
        color: #dbefff;
        margin-top: 12px;
    }

    .vlg-section {
        margin-top: 24px;
    }

    .vlg-section-title {
        font-size: 20px;
        margin: 0 0 6px;
        font-family: 'Playfair Display', Georgia, serif;
    }

    .vlg-section-subtitle {
        margin: 0 0 16px;
        font-size: 13px;
        color: var(--vlg-text-muted);
    }

    .vlg-label {
        display: block;
        font-size: 13px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--vlg-text-muted);
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(9, 10, 15, 0.9);
        border-radius: 999px;
        padding: 4px;
        border: 1px solid var(--vlg-border-subtle);
        gap: 4px;
        justify-content: flex-start;
        margin-bottom: 0;
    }

    .stTabs [role="tab"] {
        border: none;
        border-radius: 999px;
        padding: 8px 18px;
        color: var(--vlg-text-muted);
        background: transparent;
        gap: 8px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--vlg-accent), var(--vlg-accent-strong)) !important;
        color: #1a1a1a !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
        font-weight: 600;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stFileUploader"] label {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--vlg-text-muted);
    }

    div[data-testid="stSelectbox"] > div,
    div[data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid var(--vlg-border-subtle);
        background: var(--vlg-bg-soft);
        color: var(--vlg-text);
    }

    textarea, input[type="text"] {
        background: var(--vlg-bg-soft) !important;
        border: 1px solid var(--vlg-border-subtle) !important;
        border-radius: 12px !important;
        color: var(--vlg-text) !important;
    }

    textarea:focus, input[type="text"]:focus {
        border-color: var(--vlg-accent) !important;
        box-shadow: 0 0 0 1px rgba(249, 196, 107, 0.4);
    }

    div[data-testid="stFileUploader"] > div {
        border: 1px dashed rgba(148, 153, 170, 0.8);
        border-radius: 16px;
        background: rgba(13, 17, 26, 0.95);
        padding: 16px;
    }

    .reading-pane-wrapper {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px;
        background: rgba(22, 24, 34, 0.9);
        max-height: 520px;
        min-height: 520px;
        overflow-y: auto;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    }

    .reading-pane-wrapper::-webkit-scrollbar {
        width: 8px;
    }

    .reading-pane-wrapper::-webkit-scrollbar-thumb {
        background-color: rgba(249, 196, 107, 0.5);
        border-radius: 4px;
    }

    .interactive-reading {
        color: var(--vlg-text);
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .selected-passage-card {
        border-radius: 16px;
        padding: 16px;
        background: rgba(249, 196, 107, 0.08);
        border: 1px solid rgba(249, 196, 107, 0.25);
        font-size: 0.9rem;
    }

    .selected-label {
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        color: var(--vlg-text-muted);
        margin-bottom: 6px;
    }

    .empty-state-card {
        border-radius: 14px;
        border: 1px dashed rgba(255, 255, 255, 0.2);
        padding: 18px;
        text-align: center;
        color: var(--vlg-text-muted);
    }

    .guide-message {
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .guide-message.user-message {
        background: rgba(79, 208, 255, 0.08);
        border: 1px solid rgba(79, 208, 255, 0.3);
    }

    .guide-message.vonnegut-message {
        background: rgba(249, 196, 107, 0.08);
        border: 1px solid rgba(249, 196, 107, 0.25);
    }

    .sim-note {
        color: var(--vlg-text-muted);
    }

    .upload-hint {
        font-size: 0.85rem;
        color: var(--vlg-text-muted);
        margin-bottom: 6px;
    }

    .stButton>button {
        border-radius: 999px;
        border: none;
        padding: 10px 20px;
        background: linear-gradient(135deg, var(--vlg-accent), var(--vlg-accent-strong));
        color: #1a1a1a;
        font-weight: 600;
        transition: transform var(--vlg-transition-fast), box-shadow var(--vlg-transition-fast);
    }

    .stButton>button:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    }

    .stButton>button:disabled {
        opacity: 0.4;
    }

    .stCheckbox label {
        color: var(--vlg-text);
    }

    .stMarkdown code {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 6px;
        padding: 2px 6px;
    }

    .vlg-footer {
        text-align: center;
        color: var(--vlg-text-muted);
        font-size: 0.85rem;
        margin-top: 32px;
    }

    @media (max-width: 768px) {
        .vlg-header {
            padding-top: 18px;
        }
        .vlg-title {
            font-size: 34px;
        }
        .vlg-card {
            padding: 20px;
        }
        .main .block-container {
            padding-left: 16px;
            padding-right: 16px;
        }
    }
    </style>
    
    <!-- Video Background -->""" + ("""
    <video class="video-background" autoplay muted loop>
        <source src="data:video/mp4;base64,""" + get_video_base64() + """" type="video/mp4">
    </video>""" if get_video_base64() else "") + """
    """, unsafe_allow_html=True)



    st.markdown("<div class='vlg-root'>", unsafe_allow_html=True)
    st.markdown(
        """
        <header class="vlg-header">
            <div class="vlg-header-inner">
                <h1 class="vlg-title">Vonnebot</h1>
                <p class="vlg-quote">A Kurt Vonnegut Inspired Reading Companion</p>
                <p class="vlg-tagline">"Listen. If this isn't nice, what is?"</p>
            </div>
        </header>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<main class='vlg-main'>", unsafe_allow_html=True)

    # Password protection
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<section class='vlg-card'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="vlg-section">
                <h2 class="vlg-section-title">Unlock the reading room</h2>
                <p class="vlg-section-subtitle">Enter the shared passcode to keep this demo private.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        password = st.text_input("Enter passcode:", type="password")
        if st.button("Enter"):
            if password == "tralfamadore":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong passcode. So it goes.")
        st.markdown("</section>", unsafe_allow_html=True)
        st.markdown("</main></div>", unsafe_allow_html=True)
        return

    # Initialize session state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "learning_history" not in st.session_state:
        st.session_state.learning_history = []
    if "selected_passage" not in st.session_state:
        st.session_state.selected_passage = None

    if "followup_question" not in st.session_state:
        st.session_state.followup_question = ""

    if "enable_avatar" not in st.session_state:
        st.session_state.enable_avatar = True

    if "interaction_mode" not in st.session_state:
        st.session_state.interaction_mode = "Text"  # Options: "Text", "Talk"

    with st.sidebar:
        render_profile_settings(key_prefix="sidebar_profile_")

    # Tabs for different modes
    tabs_shell = st.container()
    with tabs_shell:
        tab1, tab2 = st.tabs(["💬 Chat with Kurt", "📖 Interactive Reading Guide"])

    with tab1:
        st.markdown("<section class='vlg-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='vlg-section-subtitle'>Classic chat mode with optional audio replies.</div>",
            unsafe_allow_html=True
        )
        if st.button("Clear sessions", key="clear_all_conversations"):
            st.session_state.conversation_history = []
            st.session_state.learning_history = []
            st.session_state.selected_passage = None
            st.session_state.followup_question = ""
            st.rerun()
        chat_interface()
        st.markdown("</section>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<section class='vlg-card'>", unsafe_allow_html=True)
        learning_guide_interface()
        st.markdown("</section>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="vlg-footer">
            <p style="margin-bottom: 12px;">"So it goes."</p>
            <details style="max-width: 600px; margin: 0 auto; text-align: left;">
                <summary style="cursor: pointer; color: var(--vlg-accent);">About Vonnebot</summary>
                <p style="margin-top: 10px; font-size: 0.85rem; line-height: 1.5;">
                    Vonnebot is an AI tool trained on Kurt Vonnegut's writings to offer readers additional context and insights.
                    It's a way to engage with his work interactively—not a literal channeling of Vonnegut himself.
                    Born in 1922, he had his own views on technology; while we think he might have found this intriguing,
                    we acknowledge this is just an approximation. Our aim is to bring his literature to life for
                    contemporary readers in a dynamic way. This project is not affiliated with or endorsed by the Vonnegut estate.
                </p>
            </details>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</main>", unsafe_allow_html=True)
    st.markdown("</main>", unsafe_allow_html=True)
    # render_simli_avatar() # Now rendered inside the right column of the interface
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
