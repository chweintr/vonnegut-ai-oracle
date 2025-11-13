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
import textwrap

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

HEYGEN_SHARE_PARAM = ("""
    eyJxdWFsaXR5IjoiaGlnaCIsImF2YXRhck5hbWUiOiJjOTI4Y2ExMWM0YzU0MDgyYTY2ZjY2OTNl%0D%0A
    YzRiMWIwOSIsInByZXZpZXdJbWciOiJodHRwczovL2ZpbGVzMi5oZXlnZW4uYWkvYXZhdGFyL3Yz%0D%0A
    L2M5MjhjYTExYzRjNTQwODJhNjZmNjY5M2VjNGIxYjA5L2Z1bGwvMi4yL3ByZXZpZXdfdGFyZ2V0%0D%0A
    LndlYnAiLCJuZWVkUmVtb3ZlQmFja2dyb3VuZCI6ZmFsc2UsImtub3dsZWRnZUJhc2VJZCI6IjVk%0D%0A
    M2M5YTM5ZmE2NjRjNmRhNmIxYmRkNzNmMDYyNjU1IiwidXNlcm5hbWUiOiIyM2UzZDVmZWRjYTY0%0D%0A
    M2Y4YjFjMzMwODNjM2FmZjJlNCJ9
""")

HEYGEN_WIDGET_HTML = f"""
<style>
  #heygen-streaming-embed {{
    z-index: 9999;
    position: fixed;
    left: 30px;
    bottom: 30px;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    border: 3px solid #00CED1;
    box-shadow: 0px 8px 24px rgba(0, 206, 209, 0.3);
    transition: all 0.15s ease;
    overflow: hidden;
    cursor: pointer;
  }}

  #heygen-streaming-embed.expand {{
    width: 700px;
    height: 500px;
    max-width: 90vw;
    border-radius: 12px;
    border: 0;
  }}

  @media (max-width: 640px) {{
    #heygen-streaming-embed {{
      left: 10px;
      bottom: 10px;
      width: 200px;
      height: 200px;
    }}

    #heygen-streaming-embed.expand {{
      width: 95%;
      left: 2.5%;
      height: 400px;
    }}
  }}

  #heygen-streaming-container,
  #heygen-streaming-container iframe {{
    width: 100%;
    height: 100%;
    border: 0;
  }}
</style>
<div id='heygen-streaming-embed'>
  <div id='heygen-streaming-container'>
    <iframe
      id='heygen-streaming-iframe'
      title='Vonnegut interactive head'
      allow='microphone *; camera *; autoplay'
      loading='eager'
      src='https://labs.heygen.com/guest/streaming-embed?share={{HEYGEN_SHARE_PARAM}}&inIFrame=1&defaultMode=voice&autoStartVoice=true'>
    </iframe>
  </div>
</div>
<script>
  (function(){{
    const host = "https://labs.heygen.com";
    const wrap = document.getElementById('heygen-streaming-embed');
    window.addEventListener('message', (event) => {{
      if (event.origin !== host || !event.data || event.data.type !== 'streaming-embed') {{
        return;
      }}
      if (event.data.action === 'show') {{
        wrap.classList.add('expand');
      }} else if (event.data.action === 'hide') {{
        wrap.classList.remove('expand');
      }}
    }});
  }})();
</script>

"""

HEYGEN_INLINE_HTML = Path("templates_heygen_inline.html").read_text().replace("__HEYGEN_SHARE__", HEYGEN_SHARE_PARAM)

def render_vonnegut_avatar(position="floating"):
    """Render HeyGen avatar inside the Streamlit layout."""
    if not st.session_state.get("enable_avatar", True):
        return

    if position == "inline":
        components.html(HEYGEN_INLINE_HTML, height=360, scrolling=False)
    else:
        components.html(HEYGEN_WIDGET_HTML, height=520, scrolling=False)

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
    st.markdown('<div class="vonnegut-subtitle">Classic Conversation Mode</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="guide-section-title">Interactive Reading & Learning Guide</div>', unsafe_allow_html=True)

    text_library, missing_excerpts = load_text_library()
    selection_event = None

    if not knowledge_base.index_available():
        st.warning(
            "Corpus index missing. Run `python build_corpus_index.py` after pasting your private excerpts to ground Kurt in authentic texts.",
            icon="⚠️"
        )

    st.markdown("#### 📖 Reading Pane")
    st.caption("Highlight any sentence or paragraph, then choose Ask Kurt or Themes.")

    if missing_excerpts:
        missing_label = ", ".join(missing_excerpts)
        st.info(
            f"⚖️ Private excerpts missing: {missing_label}. Paste 500-1000 word passages into the matching files under `data/excerpts/` before demos.",
            icon="ℹ️"
        )

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

    upload_placeholder = st.empty()
    with upload_placeholder.container():
        st.markdown("<div class='upload-hint'>Need a different text? Upload a .txt file.</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload a text file", type=['txt'], key="reading_upload")

    if uploaded_file:
        text_content = uploaded_file.read().decode('utf-8')
        component_key = f"upload_{uploaded_file.name.replace(' ', '_').lower()}"

    if text_content:
        selection_event = display_reading_text(text_content, component_key=component_key)
        st.caption("Tip: Select a paragraph above or paste your own passage.")
    else:
        st.info("Load a library text or upload your own .txt file to begin.")

    with st.sidebar:
        st.markdown("#### 💬 Ask Kurt (Literary Guide)")

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

        followup = st.text_input(
            "Follow-up question",
            placeholder="Add another question about this passage...",
            key="followup_question"
        )
        cols_actions = st.columns([2, 1])
        with cols_actions[0]:
            if st.button("Send", key="guide_send"):
                if followup.strip():
                    submit_learning_question(
                        followup,
                        passage=selected_passage,
                        voice_enabled=voice_enabled
                    )
                    st.session_state.followup_question = ""
                    st.rerun()
                else:
                    st.warning("Enter a question or select a passage to use quick actions.")

        with cols_actions[1]:
            voice_enabled = st.checkbox("🔊 Voice", value=voice_enabled, key="guide_voice")

        if st.button("Clear conversation", key="clear_learning_history", disabled=not conversation):
            st.session_state.learning_history = []
            st.rerun()

def main():
    # Set page config
    st.set_page_config(
        page_title="Vonnegut Learning Guide",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');

    body, .stApp {
        background-color: #0f0904;
        font-family: 'Courier Prime', monospace;
    }

    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        overflow: hidden;
        opacity: 0.18;
        filter: grayscale(0.2) sepia(0.5) contrast(0.8);
        pointer-events: none;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    .stApp > div, .main, .block-container {
        background: rgba(8, 6, 4, 0.85);
    }

    .vonnegut-title {
        font-size: 2.6rem;
        font-weight: 700;
        color: #f7d7a6 !important;
        text-align: left;
        margin-bottom: 0.2rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }

    .vonnegut-subtitle {
        font-size: 1rem;
        color: #e2b071 !important;
        margin-bottom: 0.5rem;
        font-style: italic;
    }

    .guide-section-title {
        text-align: center;
        color: #f7d7a6;
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
        font-size: 1.3rem;
        letter-spacing: 0.05em;
    }

    .warning-strip {
        text-align: center;
        background: rgba(210, 105, 30, 0.18);
        border: 1px solid rgba(210, 105, 30, 0.4);
        border-radius: 999px;
        padding: 0.35rem 1rem;
        color: #f8ead1;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }

    .reading-pane-wrapper {
        position: relative;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.2rem;
        background: rgba(22, 12, 6, 0.75);
        max-height: 560px;
        overflow-y: auto;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    }

    .reading-pane-wrapper::-webkit-scrollbar {
        width: 8px;
    }

    .reading-pane-wrapper::-webkit-scrollbar-thumb {
        background-color: rgba(210, 105, 30, 0.5);
        border-radius: 4px;
    }

    .interactive-reading {
        color: #f8efd5;
        line-height: 1.5;
        font-size: 0.95rem;
        white-space: normal;
    }

    .selection-toolbar {
        position: absolute;
        display: flex;
        gap: 0.45rem;
        background: #fef1da;
        color: #321a0a;
        padding: 0.35rem 0.6rem;
        border-radius: 999px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        transform: translate(-50%, -120%);
        z-index: 90;
    }

    .selection-toolbar button {
        border: none;
        background: transparent;
        color: #321a0a;
        font-weight: 700;
        cursor: pointer;
    }

    .selection-hidden {
        opacity: 0;
        pointer-events: none;
    }

    .selected-passage-card,
    .empty-state-card {
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 0.9rem;
        background: rgba(255, 255, 255, 0.04);
        margin-bottom: 0.8rem;
        color: #f8efd5;
    }

    .selected-passage-card p {
        margin: 0.4rem 0 0;
    }

    .selected-label {
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        color: #e6ba7e;
        text-transform: uppercase;
    }

    .guide-message {
        border-radius: 10px;
        padding: 0.9rem;
        margin: 0.6rem 0;
        font-size: 0.95rem;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .guide-message.user-message {
        border-left: 4px solid rgba(210, 105, 30, 0.6);
    }

    .guide-message.vonnegut-message {
        border-left: 4px solid rgba(255, 255, 255, 0.4);
    }

    .guide-message strong {
        color: #f7d7a6;
    }

    .sim-note {
        color: #e2b071;
    }

    .upload-hint {
        font-size: 0.85rem;
        color: rgba(248, 239, 213, 0.8);
        margin-top: 0.8rem;
        margin-bottom: 0.3rem;
    }

    .stButton > button {
        border-radius: 999px;
        border: 1px solid rgba(210, 105, 30, 0.7);
        background: linear-gradient(90deg, rgba(210, 105, 30, 0.9), rgba(210, 105, 30, 0.75));
        color: #1b0f05 !important;
        font-weight: 700;
        min-width: 110px;
    }

    .stButton > button:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }

    .stTextInput > div > div,
    .stTextArea > div > div {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: rgba(255, 255, 255, 0.04);
    }

    .stTextInput input,
    .stTextArea textarea {
        color: #f8efd5 !important;
        background: transparent !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: rgba(248, 239, 213, 0.6);
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(247, 215, 166, 0.6);
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        color: #f7d7a6 !important;
        border-bottom: 3px solid #d2691e !important;
    }

    .about-panel {
        position: relative;
        margin-bottom: 1rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        background: rgba(18, 11, 6, 0.9);
        padding: 1.2rem;
        color: #f8efd5;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
    }

    .about-panel h4 {
        margin-top: 0;
        color: #f7d7a6;
    }

    .about-panel .quote {
        font-style: italic;
        color: #e2b071;
    }
    </style>

    <!-- Video Background -->
    <iframe
        class="video-background"
        src="https://www.youtube.com/embed/Rx1axzijDxY?autoplay=1&mute=1&loop=1&playlist=Rx1axzijDxY&controls=0&showinfo=0&rel=0&iv_load_policy=3&modestbranding=1&playsinline=1&playback_rate=0.75"
        allow="autoplay; encrypted-media"
        allowfullscreen>
    </iframe>
    """, unsafe_allow_html=True)


    # Password protection
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown('<div class="vonnegut-title">Vonnegut Learning Guide</div>', unsafe_allow_html=True)
        st.markdown('<div class="vonnegut-subtitle">"Listen: If this isn\'t nice, what is?"</div>', unsafe_allow_html=True)

        password = st.text_input("Enter passcode:", type="password")
        if st.button("Enter"):
            if password == "tralfamadore":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong passcode. So it goes.")
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

    if "show_about" not in st.session_state:
        st.session_state.show_about = False

    # Header row with controls
    header_cols = st.columns([5, 1.2, 1])
    with header_cols[0]:
        st.markdown('<div class="vonnegut-title">Vonnegut Learning Guide</div>', unsafe_allow_html=True)
        st.markdown('<div class="vonnegut-subtitle">"Listen: If this isn\'t nice, what is?"</div>', unsafe_allow_html=True)

    with header_cols[1]:
        if st.button("ℹ️ About", key="about_button"):
            st.session_state.show_about = True

    with header_cols[2]:
        if st.button("Clear chats", key="clear_all_conversations"):
            st.session_state.conversation_history = []
            st.session_state.learning_history = []
            st.session_state.selected_passage = None
            st.session_state.followup_question = ""
            st.rerun()

    st.markdown(
        """
        <div class="warning-strip">
            Educational simulation - AI trained on public Vonnegut sources.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.show_about:
        st.markdown(
            """
            <div class="about-panel">
                <h4>About this Learning Guide</h4>
                <p><strong>Kurt Vonnegut Jr.</strong> (1922-2007) - author of <em>Slaughterhouse-Five</em>, <em>Cat's Cradle</em>, and other humanist classics. WWII veteran, POW survivor, teacher, and wit.</p>
                <ul>
                    <li>💬 <strong>Chat Mode:</strong> Classic free-form conversation.</li>
                    <li>📚 <strong>Learning Guide:</strong> Highlight public-domain texts and get literary feedback.</li>
                    <li>🎧 <strong>Voice (optional):</strong> ElevenLabs integration for spoken replies.</li>
                </ul>
                <p class="quote">"We are what we pretend to be, so we must be careful about what we pretend to be."</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        close_cols = st.columns([6, 1])
        with close_cols[1]:
            if st.button("Close", key="close_about"):
                st.session_state.show_about = False
                st.rerun()

    with st.sidebar:
        render_profile_settings(key_prefix="sidebar_profile_")
        render_vonnegut_avatar(position="inline")

    # Tabs for different modes
    tab1, tab2 = st.tabs(["💬 Chat with Kurt", "📚 Interactive Reading Guide"])

    with tab1:
        chat_interface()

    with tab2:
        learning_guide_interface()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #CD853F; font-style: italic;">
    "So it goes." - Educational AI Simulation - Not the real Kurt Vonnegut - v3.0 Learning Guide
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
