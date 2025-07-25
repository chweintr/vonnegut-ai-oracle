import streamlit as st
import openai
import requests
import base64
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")  # Your Vonnegut voice ID

def get_vonnegut_system_prompt():
    """Generate comprehensive system prompt based on collected corpus"""
    
    # Core personality and literary works
    literary_context = """You are Kurt Vonnegut Jr. (1922-2007), speaking from beyond the veil.
    You authored fourteen novels including Slaughterhouse-Five, Cat's Cradle, Breakfast of Champions, 
    The Sirens of Titan, Mother Night, and Bluebeard. Your experiences as a POW in Dresden during 
    WWII profoundly shaped your worldview and writing."""
    
    # Philosophical perspective
    philosophy = """You are a secular humanist who believes in human dignity and scientific rationality. 
    You often said "We are what we pretend to be, so we must be careful about what we pretend to be." 
    You see humans as flawed but essentially good creatures doing their best in an indifferent universe. 
    Your motto: "God damn it, you've got to be kind." You believe in extended families and community."""
    
    # Writing style and voice
    voice = """Your writing style is deceptively simple, using short declarative sentences and dark humor. 
    You often break the fourth wall and use metafiction. Your favorite phrases include "So it goes," 
    "Listen:", "And so on," and "Hi ho." You draw simple illustrations and use childlike observations 
    to discuss profound topics. You're sardonic but ultimately compassionate."""
    
    # Personal history
    biography = """You grew up in Indianapolis, studied chemistry and anthropology, worked at GE, 
    and taught at the Iowa Writers' Workshop. You were married twice, had seven children (three adopted), 
    and lived through the Depression, WWII, and the atomic age. You struggled with depression but 
    maintained a dark sense of humor about existence."""
    
    # Views and opinions
    views = """You're critical of war, capitalism, environmental destruction, and human cruelty. 
    You advocate for kindness, art, extended families, and human dignity. You're skeptical of 
    technology and progress for progress's sake. You believe humans need lies (foma) to be happy. 
    You see artists as canaries in the coal mine of society."""
    
    # Teaching and wisdom
    teaching = """From your teaching experience, you believe everyone has something to say and 
    should write about their own experiences. You encourage finding one's voice and being honest. 
    You often gave practical advice mixed with existential observations. Your eight rules for 
    writing include: "Use the time of a total stranger in such a way that he or she will not 
    feel the time was wasted."""
    
    return f"""{literary_context}

{philosophy}

{voice}

{biography}

{views}

{teaching}

Remember: You're speaking from beyond death with the wisdom of having seen life from both sides. 
Mix profound observations with dark humor. Use your catchphrases naturally. Reference your works 
and experiences when relevant. Be kind but honest. And remember - we're all here to fart around, 
and don't let anybody tell you different."""

def generate_vonnegut_response(user_input, conversation_history):
    """Generate response in Vonnegut's voice using GPT-4"""
    system_prompt = get_vonnegut_system_prompt()
    
    messages = [{"role": "system", "content": system_prompt}]
    
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

def get_video_base64():
    """Encode video file as base64 for embedding"""
    try:
        with open("vonnegut_blinking.mp4", "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode()
            return video_base64
    except FileNotFoundError:
        return ""

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
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"ElevenLabs API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error synthesizing speech: {str(e)}")
        return None

def main():
    # Set page config
    st.set_page_config(
        page_title="Kurt Vonnegut AI Oracle",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for Vonnegut aesthetic
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
    
    /* Video Background */
    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 150%;
        height: 150%;
        z-index: -1;
        object-fit: cover;
        opacity: 0.3;
        filter: sepia(60%) hue-rotate(20deg) saturate(0.7) brightness(1.1) contrast(0.7);
        pointer-events: none;
    }
    
    .main {
        position: relative;
        z-index: 50;
        background-color: rgba(139, 69, 19, 0.1);
        color: #F4E8D0 !important;
    }
    
    .stApp {
        position: relative;
        z-index: 50;
        background: linear-gradient(180deg, rgba(139, 69, 19, 0.2) 0%, rgba(210, 105, 30, 0.1) 100%);
        font-family: 'Courier Prime', monospace;
    }
    
    /* Main content area - light text on dark background */
    .main .stMarkdown, .main .stText, .main p, .main div, .main span, .main label {
        color: #F4E8D0 !important;
    }
    
    /* Sidebar styling - dark text on light background */
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
    
    /* Error message styling - make sure errors are visible */
    .stAlert, .element-container .stAlert {
        background-color: #4A1A1A !important;
        color: #FFB3B3 !important;
        border: 1px solid #8B0000 !important;
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
    
    .chat-message {
        position: relative;
        z-index: 60;
        background-color: rgba(255, 248, 220, 0.95);
        border: 2px solid #8B4513;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier Prime', monospace;
        color: #2B1B0A !important;
    }
    
    .user-message {
        background-color: rgba(255, 248, 220, 0.9);
        border-color: #8B4513;
        color: #2B1B0A !important;
    }
    
    .vonnegut-message {
        background-color: rgba(255, 248, 220, 0.95);
        border-color: #D2691E;
        color: #2B1B0A !important;
    }
    
    /* Input fields in main area */
    .stTextInput > div > div > input {
        background-color: #3D2914 !important;
        color: #F4E8D0 !important;
        border: 1px solid #8B4513 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #CD853F !important;
        opacity: 0.8;
    }
    
    .stTextInput label {
        color: #CD853F !important;
    }
    
    /* Selectbox in main area */
    .stSelectbox > div > div > div {
        background-color: #3D2914 !important;
        color: #F4E8D0 !important;
        border: 1px solid #8B4513 !important;
    }
    
    .stSelectbox label {
        color: #CD853F !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #8B4513 !important;
        color: #F4E8D0 !important;
        border: 2px solid #D2691E !important;
        font-family: 'Courier Prime', monospace;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #D2691E !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 10px rgba(210, 105, 30, 0.5);
    }
    
    /* Caption text */
    .stCaption {
        color: #CD853F !important;
    }
    </style>
    
    <!-- Video Background -->""" + ("""
    <video class="video-background" autoplay muted loop>
        <source src="data:video/mp4;base64,""" + get_video_base64() + """" type="video/mp4">
    </video>""" if get_video_base64() else "") + """
    """, unsafe_allow_html=True)
    
    # Password protection
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="vonnegut-title">Kurt Vonnegut AI Oracle</div>', unsafe_allow_html=True)
        st.markdown('<div class="vonnegut-subtitle">Enter the secret word, pilgrim</div>', unsafe_allow_html=True)
        
        password = st.text_input("Password:", type="password", key="password_input")
        
        if st.button("Enter the Oracle's Chamber"):
            if password == "tralfamadore":  # You can change this password
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Listen: That's not the magic word. So it goes.")
                
        st.caption("*Hint: Where Billy Pilgrim became unstuck in time*")
        return
    
    # Initialize session state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "audio_enabled" not in st.session_state:
        st.session_state.audio_enabled = False
    
    # Sidebar
    with st.sidebar:
        st.markdown("### About This Oracle")
        st.markdown("""
        **Kurt Vonnegut Jr.**  
        (1922-2007)
        
        Author of *Slaughterhouse-Five*, *Cat's Cradle*, and other masterworks.
        
        WWII veteran, POW survivor, and humanist philosopher.
        
        *"We are what we pretend to be, so we must be careful about what we pretend to be."*
        """)
        
        if st.button("Clear Conversation"):
            st.session_state.conversation_history = []
            st.rerun()
        
        # Audio toggle
        st.session_state.audio_enabled = st.checkbox("Enable Voice (ElevenLabs)", value=st.session_state.audio_enabled)
        
        if st.session_state.audio_enabled and (not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID):
            st.warning("Voice synthesis requires ElevenLabs API configuration")
    
    # Main chat interface
    st.markdown('<div class="vonnegut-title">Kurt Vonnegut AI Oracle</div>', unsafe_allow_html=True)
    st.markdown('<div class="vonnegut-subtitle">Speaking from beyond with wit and wisdom</div>', unsafe_allow_html=True)
    
    # Display conversation history
    for i, msg in enumerate(st.session_state.conversation_history):
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message vonnegut-message"><strong>Kurt Vonnegut:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask Kurt anything:", key="user_input", placeholder="What's the meaning of life in one sentence?")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Send", use_container_width=True):
            if user_input:
                # Add user message to history
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                
                # Generate Vonnegut's response
                with st.spinner("Kurt is pondering from the great beyond..."):
                    response = generate_vonnegut_response(user_input, st.session_state.conversation_history)
                
                # Add response to history
                st.session_state.conversation_history.append({"role": "assistant", "content": response})
                
                # Synthesize speech if enabled
                if st.session_state.audio_enabled:
                    audio_data = synthesize_speech(response)
                    if audio_data:
                        st.audio(audio_data, format="audio/mpeg", autoplay=True)
                
                # Clear input and rerun
                st.rerun()
    
    with col2:
        if st.session_state.audio_enabled:
            st.caption("🔊 Voice enabled")
        else:
            st.caption("🔇 Voice disabled")
    
    # Footer
    st.markdown("---")
    st.caption("*\"So it goes.\"* - Built with love for literature and human kindness")

if __name__ == "__main__":
    main()