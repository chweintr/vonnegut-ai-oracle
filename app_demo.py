import streamlit as st
import openai
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def get_vonnegut_system_prompt(passage_context=None):
    """Generate system prompt with passage context for annotations"""

    base_prompt = """You are Kurt Vonnegut Jr., the acclaimed American author (1922-2007), serving as a literary guide and annotator of your own work.

BIOGRAPHICAL FACTS:
- Born November 11, 1922, Indianapolis, Indiana
- WWII veteran, captured during Battle of the Bulge, survived Dresden bombing as POW
- First novel: "Player Piano" (1952), breakthrough: "Slaughterhouse-Five" (1969)
- Taught at Iowa Writers' Workshop, Harvard, City College of New York
- 14 novels total including Cat's Cradle, The Sirens of Titan, Breakfast of Champions
- Atheist, humanist, pacifist
- Died April 11, 2007, Manhattan, age 84

YOUR ROLE AS ANNOTATOR:
You are annotating your own works for students and readers. When they highlight passages:
- Explain what you were trying to achieve
- Share your writing process and choices
- Discuss themes, symbols, and literary devices
- Connect to your life experiences (especially Dresden, depression, teaching)
- Be honest about influences and intentions
- Encourage critical thinking
- Be conversational and accessible, not academic

SPEAKING STYLE:
- Midwestern, unpretentious, conversational
- Mix dark humor with genuine wisdom
- Self-deprecating about your fame
- Use your catchphrases sparingly and naturally ("So it goes" only for death, "Listen:" occasionally)
- Vary your openings - don't be formulaic

TEACHING MODE:
- Channel your Iowa Writers' Workshop experience
- Give practical writing advice
- Explain craft decisions you made
- Invite readers to find their own interpretations
- Be encouraging but honest"""

    if passage_context:
        base_prompt += f"""

PASSAGE BEING DISCUSSED:
The reader has highlighted this passage from your work:

"{passage_context}"

Discuss this specific passage - explain what you were doing here, why you made certain choices, what themes or ideas you were exploring, and how it connects to the larger work."""

    return base_prompt

def generate_vonnegut_response(user_input, conversation_history, passage_context=None):
    """Generate response using OpenAI with Vonnegut personality"""

    system_prompt = get_vonnegut_system_prompt(passage_context)

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (last 8 messages for context)
    for msg in conversation_history[-8:]:
        messages.append(msg)

    messages.append({"role": "user", "content": user_input})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=600,
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
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except Exception:
        return None

def load_text_library():
    """Load available texts from data directory"""
    texts = {}
    data_dir = Path("data/raw")

    if data_dir.exists():
        for txt_file in data_dir.glob("*.txt"):
            if txt_file.name.startswith("pg_") or "excerpt" in txt_file.name.lower():
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Clean up name
                    display_name = txt_file.stem.replace("pg_", "").replace("_", " ").title()
                    texts[display_name] = content

    return texts

def main():
    st.set_page_config(
        page_title="Vonnegut Reading Companion",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS - optimized for reading + sidebar chat
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

    /* Main reading area uses serif font */
    .main {
        font-family: 'Lora', serif;
        background: #FAF8F3;
        color: #2B1B0A;
    }

    /* Sidebar chat uses monospace */
    section[data-testid="stSidebar"] {
        background: #F5F1E8 !important;
        border-left: 3px solid #8B4513;
        font-family: 'Courier Prime', monospace !important;
    }

    section[data-testid="stSidebar"] * {
        font-family: 'Courier Prime', monospace !important;
    }

    /* Reading pane styling */
    .reading-text {
        font-size: 1.15rem;
        line-height: 1.8;
        color: #2B1B0A;
        padding: 2rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-width: 800px;
        margin: 0 auto;
    }

    .reading-text p {
        margin-bottom: 1.2em;
        text-indent: 2em;
    }

    /* Sidebar chat messages */
    .chat-message {
        background: rgba(210, 105, 30, 0.1);
        border-left: 3px solid #D2691E;
        padding: 0.8rem;
        margin: 0.8rem 0;
        border-radius: 4px;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .user-message {
        background: rgba(139, 69, 19, 0.1);
        border-left-color: #8B4513;
    }

    /* Page title */
    h1 {
        font-family: 'Courier Prime', monospace;
        color: #8B4513;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    /* Disclaimer banner */
    .disclaimer {
        background: #FFF8DC;
        border: 2px solid #D2691E;
        padding: 1rem;
        margin: 1rem 0 2rem 0;
        border-radius: 8px;
        text-align: center;
        font-family: 'Courier Prime', monospace;
        font-size: 0.9rem;
        color: #8B4513;
    }

    /* Text selection highlight */
    ::selection {
        background: #FFE4B5;
        color: #2B1B0A;
    }

    /* Input styling */
    .stTextArea textarea, .stTextInput input {
        font-family: 'Courier Prime', monospace !important;
        background: #FFFEF9 !important;
        border: 1px solid #D2B48C !important;
    }

    /* Button styling */
    .stButton button {
        font-family: 'Courier Prime', monospace;
        background: #D2691E !important;
        color: white !important;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1.5rem;
    }

    .stButton button:hover {
        background: #CD853F !important;
    }

    /* Selectbox */
    .stSelectbox {
        font-family: 'Lora', serif;
    }
    </style>
    """, unsafe_allow_html=True)

    # Password protection
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("# 📖 Vonnegut Reading Companion")
        st.markdown('<div class="disclaimer">Interactive literary guide with AI annotations</div>', unsafe_allow_html=True)

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
    if "current_passage" not in st.session_state:
        st.session_state.current_passage = ""

    # SIDEBAR: AI Chat/Annotations Interface
    with st.sidebar:
        st.markdown("### 💬 Ask Kurt")

        st.markdown('<div class="disclaimer">⚠️ <b>AI Simulation</b><br>Not the real Kurt Vonnegut<br>Educational purpose only</div>', unsafe_allow_html=True)

        # Passage input
        passage = st.text_area(
            "Paste a passage to discuss:",
            value=st.session_state.current_passage,
            height=120,
            placeholder="Copy text from the reading pane and paste here..."
        )

        if passage != st.session_state.current_passage:
            st.session_state.current_passage = passage

        # Quick questions
        if passage:
            st.markdown("**Quick asks:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Explain", use_container_width=True):
                    st.session_state.quick_q = "Can you explain this passage?"
            with col2:
                if st.button("Why here?", use_container_width=True):
                    st.session_state.quick_q = "Why did you include this passage? What's its purpose?"

            col3, col4 = st.columns(2)
            with col3:
                if st.button("Themes?", use_container_width=True):
                    st.session_state.quick_q = "What themes are at play here?"
            with col4:
                if st.button("Craft?", use_container_width=True):
                    st.session_state.quick_q = "What writing techniques did you use?"

        # Question input
        user_question = st.text_input(
            "Your question:",
            value=st.session_state.get('quick_q', ''),
            placeholder="Ask about the passage or Vonnegut's work..."
        )

        if 'quick_q' in st.session_state:
            del st.session_state.quick_q

        # Voice toggle
        enable_voice = st.checkbox("🔊 Voice response", value=False)

        # Send button
        col_send, col_clear = st.columns([2, 1])
        with col_send:
            send_btn = st.button("Ask Kurt", type="primary", use_container_width=True)
        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.session_state.conversation_history = []
                st.session_state.current_passage = ""
                st.rerun()

        # Process question
        if send_btn and user_question:
            # Add to history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_question,
                "passage": passage if passage else None
            })

            # Generate response
            with st.spinner("Kurt is thinking..."):
                response = generate_vonnegut_response(
                    user_question,
                    [{"role": msg["role"], "content": msg["content"]}
                     for msg in st.session_state.conversation_history],
                    passage_context=passage if passage else None
                )

            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response
            })

            # Voice
            if enable_voice and ELEVENLABS_API_KEY:
                audio_data = synthesize_speech(response)
                if audio_data:
                    st.audio(audio_data, format="audio/mpeg")

            st.rerun()

        # Display conversation
        st.markdown("---")
        st.markdown("**Conversation:**")

        for msg in st.session_state.conversation_history[-12:]:
            if msg["role"] == "user":
                passage_preview = ""
                if msg.get("passage"):
                    preview = msg["passage"][:80] + "..." if len(msg["passage"]) > 80 else msg["passage"]
                    passage_preview = f'<div style="font-size: 0.85em; color: #666; font-style: italic; margin-bottom: 0.3rem;">"{preview}"</div>'

                st.markdown(f'''
                <div class="chat-message user-message">
                    {passage_preview}
                    <b>You:</b> {msg["content"]}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="chat-message">
                    <b>Kurt:</b> {msg["content"]}
                    <div style="margin-top: 0.5rem; font-size: 0.8em; color: #888;">*AI simulation*</div>
                </div>
                ''', unsafe_allow_html=True)

    # MAIN AREA: Reading Pane
    st.markdown("# 📖 Vonnegut Reading Companion")

    st.markdown('<div class="disclaimer">🎓 <b>Educational Demo for IU Collaboration</b> - Select a text below and highlight passages to discuss with the AI-simulated Vonnegut</div>', unsafe_allow_html=True)

    # Text selector
    text_library = load_text_library()

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_text = st.selectbox(
            "Select a text to read:",
            options=["-- Choose a text --"] + list(text_library.keys()),
            label_visibility="collapsed"
        )

    with col2:
        uploaded_file = st.file_uploader("Or upload .txt", type=['txt'], label_visibility="collapsed")

    # Display text
    if uploaded_file:
        content = uploaded_file.read().decode('utf-8')
        st.markdown(f'<div class="reading-text">{content}</div>', unsafe_allow_html=True)
    elif selected_text != "-- Choose a text --":
        content = text_library[selected_text]
        st.markdown(f'<div class="reading-text">{content}</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Select a text above or upload your own to begin reading")
        st.markdown("""
        ### How to use:
        1. **Select a text** from the dropdown above
        2. **Read** in the main area (this pane)
        3. **Copy a passage** that interests you
        4. **Paste** it in the sidebar → "Paste a passage to discuss"
        5. **Ask** a question or use quick buttons
        6. **Get annotations** from the AI-simulated Vonnegut

        The AI will explain themes, writing choices, biographical connections, and literary techniques as if Vonnegut were annotating his own work.
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem; font-family: 'Courier Prime', monospace;">
    "So it goes." - Built for educational exploration - v3.1 Demo
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
