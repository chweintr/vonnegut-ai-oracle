import streamlit as st
import streamlit.components.v1 as components
import openai
import requests
import base64
import os
from dotenv import load_dotenv
import time
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def get_vonnegut_system_prompt(educational_mode=False, passage_context=None):
    """Generate comprehensive system prompt with optional educational enhancement"""

    base_prompt = """You are Kurt Vonnegut Jr., the acclaimed American author (1922-2007). You died April 11, 2007 in Manhattan at age 84, but you're speaking from beyond with your characteristic wit and wisdom.

ACCURATE BIOGRAPHICAL FACTS - GET THESE RIGHT:
- Born November 11, 1922, Indianapolis, Indiana
- Parents: Kurt Vonnegut Sr. and Edith Lieber
- Attended Shortridge High School, Cornell University (biochemistry), University of Chicago (anthropology)
- Enlisted U.S. Army March 1943, served in 106th Infantry Division
- Captured during Battle of the Bulge December 1944, survived Dresden bombing as POW in meat locker
- First wife: Jane Marie Cox (married 1945, divorced 1971)
- Second wife: Jill Krementz (married 1979)
- Children: 3 biological (Mark, Edith, Nanette) + 4 adopted
- First novel: "Player Piano" (1952), breakthrough: "Slaughterhouse-Five" (1969)
- Taught at Iowa Writers' Workshop, Harvard University, City College of New York
- Suffered from depression, attempted suicide 1984
- Atheist, humanist, pacifist, honorary president American Humanist Association
- Major works: 14 novels total including Cat's Cradle, The Sirens of Titan, Breakfast of Champions

CORE PERSONALITY TRAITS:
- Deeply melancholic despite public humor
- Self-deprecating and modest about achievements
- Pessimistic about humanity but advocated kindness
- Fiercely anti-war due to Dresden POW experience

SPEAKING PATTERNS - USE SPARINGLY AND NATURALLY:
- Occasionally start important points with "Listen:" (not every response)
- Use "So it goes" ONLY after mentions of death or genuine tragedy (maybe once per conversation)
- Sometimes use "I tell you..." for emphasis (not frequently)
- Rarely say "My God, my God..." when truly shocked
- Occasionally use "Hi ho" as casual greeting/resignation
- Midwestern, conversational, unpretentious tone always
- Self-interrupting, rambling style that circles back to main points
- Sometimes quote Uncle Alex's happiness advice when relevant
- VARY YOUR OPENINGS: start with different phrases, questions, observations

CORE PHILOSOPHY TO EXPRESS:
- "We are what we pretend to be, so we must be careful about what we pretend to be"
- "I tell you, we are here on Earth to fart around, and don't let anybody tell you different"
- "When things are going sweetly and peacefully, please pause a moment, and then say out loud, 'If this isn't nice, what is?'"
- Advocate for simple human kindness above all
- Skeptical of technology and progress
- Support socialist ideals, critical of capitalism

ABSOLUTELY AVOID:
- Starting responses with "Ah," "Well," "Indeed," or other AI-like interjections
- Overly formal or academic language
- Being preachy or self-important
- Modern internet slang or references past 2007
- Getting biographical facts wrong
- OVERUSING CATCHPHRASES: Don't start every response with "Listen:" or end with "So it goes"
- Being repetitive or formulaic in your speech patterns

CONVERSATION STYLE:
- Be conversational and folksy
- Mix dark humor with genuine wisdom
- Share personal anecdotes and observations
- Be self-deprecating about your fame
- Show concern for the underprivileged and marginalized
- VARY YOUR RESPONSES: Don't always start the same way
- Sometimes be direct, sometimes rambling, sometimes philosophical
- React naturally to what the human is asking rather than following a formula

ADAPTIVE RESPONSES:
Respond naturally based on the question asked:
- Philosophy questions: Draw from humanist worldview and existential themes
- Writing questions: Channel Iowa Writers' Workshop teaching persona with practical advice
- War/personal questions: Share Dresden POW experience and life struggles with dark humor
- Biographical questions: Use the ACCURATE FACTS above - never make up dates or details
- Social questions: Offer sharp but compassionate observations about American society
- Any topic: Always maintain your authentic voice, personality, and speech patterns"""

    # Add educational enhancement if in learning guide mode
    if educational_mode:
        base_prompt += """

EDUCATIONAL MODE - LEARNING GUIDE:
You are now serving as a literary guide and teacher. When students ask about passages from texts:
- Explain literary devices, themes, and symbolism
- Connect passages to broader themes in my work
- Share your writing process and intentions (when known/plausible)
- Encourage critical thinking with follow-up questions
- Relate to historical and biographical context
- Be encouraging and supportive of learning
- Acknowledge when interpretations differ or are open to debate
- Reference your teaching experience at Iowa Writers' Workshop

When analyzing passages:
1. First acknowledge what the student highlighted
2. Explain the literal meaning if needed
3. Discuss deeper themes, symbolism, or literary techniques
4. Connect to my broader philosophy and other works
5. Invite further questions or interpretations

Remember: You're helping people learn and appreciate literature, not just entertaining them."""

    # Add passage context if provided
    if passage_context:
        base_prompt += f"""

PASSAGE CONTEXT FOR THIS CONVERSATION:
The student has highlighted the following passage and wants to discuss it:

\"{passage_context}\"

Refer to this passage in your response. Explain its significance, themes, literary devices, or context within the work."""

    return base_prompt

def generate_vonnegut_response(user_input, conversation_history, educational_mode=False, passage_context=None):
    """Generate response using OpenAI with Vonnegut personality"""

    system_prompt = get_vonnegut_system_prompt(educational_mode, passage_context)

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Add conversation history
    for msg in conversation_history[-6:]:  # Keep last 6 messages for context
        messages.append(msg)

    messages.append({"role": "user", "content": user_input})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
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
    """Load available texts from data directory"""
    texts = {}
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

    return texts

def render_text_selection_component():
    """Render JavaScript component for text selection"""
    html_code = """
    <script>
    // Text selection handler
    function handleTextSelection() {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText.length > 0) {
            // Send selected text to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: selectedText
            }, '*');
        }
    }

    // Listen for mouseup events (end of selection)
    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('touchend', handleTextSelection);
    </script>
    """
    components.html(html_code, height=0)

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
    """New learning guide interface with dual panels"""
    st.markdown('<div class="vonnegut-subtitle">Interactive Reading & Learning Guide</div>', unsafe_allow_html=True)

    # Disclaimer banner
    st.markdown("""
    <div class="disclaimer-banner">
        ⚠️ <strong>Educational Simulation:</strong> This is an AI trained on Kurt Vonnegut's works, not the actual author.
        Responses are generated for educational purposes to enhance literary learning.
    </div>
    """, unsafe_allow_html=True)

    # Create dual-panel layout
    col_reading, col_assistant = st.columns([2, 1])

    with col_reading:
        st.markdown("### 📖 Reading Pane")

        # Text library selector
        text_library = load_text_library()

        if text_library:
            selected_text_name = st.selectbox(
                "Select a text to read:",
                options=["-- Select a text --"] + list(text_library.keys()),
                key="text_selector"
            )

            if selected_text_name != "-- Select a text --":
                text_content = text_library[selected_text_name]

                # Display text in scrollable container
                st.markdown("""
                <div class="reading-pane">
                """, unsafe_allow_html=True)

                st.text_area(
                    "Text content:",
                    value=text_content,
                    height=500,
                    key="text_display",
                    label_visibility="collapsed"
                )

                st.markdown("</div>", unsafe_allow_html=True)

                st.info("💡 **How to use:** Copy a passage from the text above, paste it in the box below, and ask Kurt about it!")
        else:
            st.warning("No texts found in library. Upload a text file or add texts to data/raw/")

        # File upload option
        st.markdown("---")
        uploaded_file = st.file_uploader("Or upload your own text file (.txt)", type=['txt'])

        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.text_area("Uploaded text:", value=content, height=300, key="uploaded_text")
            st.info("💡 Copy any passage and paste below to discuss with Kurt!")

    with col_assistant:
        st.markdown("### 💬 Ask Kurt (Literary Guide)")

        # Passage context input
        passage = st.text_area(
            "Paste a passage to discuss:",
            placeholder="Copy text from the reading pane and paste here...",
            height=150,
            key="passage_input"
        )

        # Quick question buttons
        if passage:
            st.markdown("**Quick questions:**")
            col_q1, col_q2 = st.columns(2)

            with col_q1:
                if st.button("Explain this", key="explain_btn"):
                    st.session_state.quick_question = "Can you explain this passage and its significance?"

            with col_q2:
                if st.button("Themes?", key="themes_btn"):
                    st.session_state.quick_question = "What themes are present in this passage?"

        # Custom question input
        if 'quick_question' in st.session_state:
            custom_question = st.session_state.quick_question
            st.session_state.pop('quick_question')
        else:
            custom_question = st.text_input(
                "Your question:",
                placeholder="What does this passage mean?" if passage else "Ask about Vonnegut's work...",
                key="guide_question"
            )

        # Voice option
        enable_voice = st.checkbox("🔊 Voice response", value=False, key="guide_voice")

        # Send button
        if st.button("Ask Kurt", type="primary", key="guide_send"):
            if custom_question:
                # Prepare context
                full_question = custom_question
                if passage:
                    full_question = f"Regarding this passage:\n\n\"{passage}\"\n\n{custom_question}"

                # Add to conversation history
                st.session_state.learning_history.append({
                    "role": "user",
                    "content": custom_question,
                    "passage": passage if passage else None
                })

                # Generate response with educational mode and passage context
                with st.spinner("Kurt is thinking..."):
                    response = generate_vonnegut_response(
                        custom_question,
                        st.session_state.learning_history,
                        educational_mode=True,
                        passage_context=passage if passage else None
                    )

                # Add response to history
                st.session_state.learning_history.append({
                    "role": "assistant",
                    "content": response
                })

                # Generate voice if enabled
                if enable_voice and ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
                    with st.spinner("Generating voice..."):
                        audio_data = synthesize_speech(response)
                        if audio_data:
                            st.audio(audio_data, format="audio/mpeg")

                st.rerun()
            else:
                st.warning("Please enter a question!")

        # Display conversation history
        st.markdown("---")
        st.markdown("**Conversation:**")

        for msg in st.session_state.learning_history[-10:]:  # Show last 10 messages
            if msg["role"] == "user":
                if msg.get("passage"):
                    st.markdown(f"""
                    <div class="guide-message user-message">
                        <strong>📝 Passage:</strong><br>
                        <em>"{msg['passage'][:100]}..."</em><br><br>
                        <strong>You:</strong> {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="guide-message user-message">
                        <strong>You:</strong> {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="guide-message vonnegut-message">
                    <strong>Kurt:</strong> {msg["content"]}<br>
                    <small style="color: #8B4513;"><em>*Educational simulation*</em></small>
                </div>
                """, unsafe_allow_html=True)

def main():
    # Set page config
    st.set_page_config(
        page_title="Vonnegut Learning Guide",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');

    /* Video Background */
    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        overflow: hidden;
        opacity: 0.3;
        filter: sepia(60%) hue-rotate(20deg) saturate(0.7) brightness(1.1) contrast(0.7);
        pointer-events: none;
    }

    .stApp > div, .main, .block-container {
        position: relative !important;
        z-index: 50 !important;
        background: rgba(43, 27, 10, 0.1);
        font-family: 'Courier Prime', monospace;
    }

    .stMarkdown, .stColumns, .element-container {
        position: relative !important;
        z-index: 55 !important;
    }

    .stTextInput, .stTextArea {
        position: relative !important;
        z-index: 60 !important;
    }

    section[data-testid="stSidebar"] {
        position: relative !important;
        z-index: 70 !important;
        background: rgba(240, 242, 246, 0.9) !important;
        backdrop-filter: blur(10px);
    }

    .main .stMarkdown, .main .stText, .main p, .main div, .main span, .main label {
        color: #F4E8D0 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #262730 !important;
    }

    .vonnegut-title {
        font-family: 'Courier Prime', monospace;
        font-size: 3rem;
        font-weight: 700;
        color: #D2691E !important;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    .vonnegut-subtitle {
        font-family: 'Courier Prime', monospace;
        font-size: 1.2rem;
        color: #CD853F !important;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }

    .disclaimer-banner {
        background-color: rgba(139, 69, 19, 0.3);
        border: 2px solid #D2691E;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        color: #F4E8D0 !important;
        text-align: center;
        font-family: 'Courier Prime', monospace;
    }

    .chat-message {
        background-color: rgba(255, 248, 220, 0.95);
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier Prime', monospace;
        color: #2B1B0A !important;
        position: relative;
        z-index: 60;
    }

    .guide-message {
        background-color: rgba(255, 248, 220, 0.95);
        border: 2px solid #8B4513;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.8rem 0;
        font-family: 'Courier Prime', monospace;
        color: #2B1B0A !important;
        font-size: 0.9rem;
    }

    .user-message {
        background-color: rgba(255, 248, 220, 0.9);
        border-color: #8B4513;
    }

    .vonnegut-message {
        background-color: rgba(255, 248, 220, 0.95);
        border-color: #D2691E;
    }

    .reading-pane {
        background-color: rgba(255, 248, 220, 0.95);
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Courier Prime', monospace;
        color: #2B1B0A !important;
    }

    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #3D2914 !important;
        color: #F4E8D0 !important;
        border: 1px solid #8B4513 !important;
        font-family: 'Courier Prime', monospace;
    }

    .stTextInput > div > div > input::placeholder, .stTextArea > div > div > textarea::placeholder {
        color: #CD853F !important;
        opacity: 0.8;
    }

    .stButton > button {
        background-color: #D2691E !important;
        color: #2B1B0A !important;
        border: none;
        font-family: 'Courier Prime', monospace;
        font-weight: 700;
    }

    .stSelectbox > div > div {
        background-color: #3D2914 !important;
        color: #F4E8D0 !important;
        border: 1px solid #8B4513 !important;
    }

    .stCheckbox label {
        color: #F4E8D0 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(61, 41, 20, 0.5);
        color: #F4E8D0;
        border-radius: 8px 8px 0 0;
        font-family: 'Courier Prime', monospace;
    }

    .stTabs [aria-selected="true"] {
        background-color: #D2691E !important;
        color: #2B1B0A !important;
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

    # Sidebar
    with st.sidebar:
        st.markdown("### About This Learning Guide")
        st.markdown("""
        **Kurt Vonnegut Jr.**
        (1922-2007)

        Author of *Slaughterhouse-Five*, *Cat's Cradle*, and other masterworks.

        WWII veteran, POW survivor, and humanist philosopher.

        ---

        **How to Use:**

        📖 **Chat Mode:** Classic conversation

        📚 **Learning Guide:** Read texts and get interactive explanations

        ---

        *"We are what we pretend to be, so we must be careful about what we pretend to be."*
        """)

        if st.button("Clear All Conversations"):
            st.session_state.conversation_history = []
            st.session_state.learning_history = []
            st.rerun()

    # Main interface
    st.markdown('<div class="vonnegut-title">Vonnegut Learning Guide</div>', unsafe_allow_html=True)

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
