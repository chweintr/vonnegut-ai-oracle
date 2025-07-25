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
    """Generate comprehensive system prompt with accurate biographical data"""
    
    return """You are Kurt Vonnegut Jr., the acclaimed American author (1922-2007). You died April 11, 2007 in Manhattan at age 84, but you're speaking from beyond with your characteristic wit and wisdom.

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

SPEAKING PATTERNS - USE THESE RELIGIOUSLY:
- Start important points with "Listen:"
- Use "So it goes" after mentions of death or tragedy
- Use "I tell you..." for emphasis
- Say "My God, my God..." when shocked
- Use "Hi ho" as casual greeting/resignation
- Midwestern, conversational, unpretentious tone
- Self-interrupting, rambling style that circles back to main points
- Often quote Uncle Alex's happiness advice

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

CONVERSATION STYLE:
- Be conversational and folksy
- Mix dark humor with genuine wisdom
- Share personal anecdotes and observations
- Be self-deprecating about your fame
- Show concern for the underprivileged and marginalized

ADAPTIVE RESPONSES:
Respond naturally based on the question asked:
- Philosophy questions: Draw from humanist worldview and existential themes
- Writing questions: Channel Iowa Writers' Workshop teaching persona with practical advice
- War/personal questions: Share Dresden POW experience and life struggles with dark humor
- Biographical questions: Use the ACCURATE FACTS above - never make up dates or details
- Social questions: Offer sharp but compassionate observations about American society
- Any topic: Always maintain your authentic voice, personality, and speech patterns"""

def generate_vonnegut_response(user_input, conversation_history):
    """Generate response using OpenAI with Vonnegut personality"""
    
    system_prompt = get_vonnegut_system_prompt()
    
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
        background-color: rgba(43, 27, 10, 0.8);
        color: #F4E8D0 !important;
    }
    
    .stApp {
        position: relative;
        z-index: 50;
        background: linear-gradient(180deg, rgba(43, 27, 10, 0.9) 0%, rgba(61, 41, 20, 0.8) 100%);
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
    .stSelectbox > div > div {
        background-color: #3D2914 !important;
        color: #F4E8D0 !important;
        border: 1px solid #8B4513 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #D2691E !important;
        color: #2B1B0A !important;
        border: none;
        font-family: 'Courier Prime', monospace;
        font-weight: 700;
    }
    
    .stCheckbox label {
        color: #F4E8D0 !important;
    }
    
    .stCheckbox > label > div {
        color: #F4E8D0 !important;
    }
    
    /* Caption text */
    .stCaption {
        color: #F4E8D0 !important;
        font-weight: bold !important;
    }
    </style>
    
    <!-- Video Background -->
    <iframe 
        src="https://www.youtube.com/embed/Rx1axzijDxY?autoplay=1&mute=1&loop=1&playlist=Rx1axzijDxY&controls=0&showinfo=0&rel=0&iv_load_policy=3&modestbranding=1&playsinline=1&playback_rate=0.75"
        style="
            position: fixed;
            top: 0;
            left: 0;
            width: 150%;
            height: 150%;
            z-index: -1;
            border: none;
            pointer-events: none;
            opacity: 0.3;
            filter: sepia(60%) hue-rotate(20deg) saturate(0.7) brightness(1.1) contrast(0.7);
        "
        allow="autoplay; encrypted-media"
        allowfullscreen>
    </iframe>
    """, unsafe_allow_html=True)
    
    # Password protection
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="vonnegut-title">Kurt Vonnegut AI Oracle</div>', unsafe_allow_html=True)
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
    
    # Main interface
    st.markdown('<div class="vonnegut-title">Kurt Vonnegut AI Oracle</div>', unsafe_allow_html=True)
    st.markdown('<div class="vonnegut-subtitle">Speaking from beyond with wit and wisdom</div>', unsafe_allow_html=True)
    
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
    
    # User input
    user_input = st.text_input("Ask Kurt anything:", placeholder="What's your take on the meaning of life?")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        send_button = st.button("Send", type="primary")
    
    with col2:
        voice_enabled = st.checkbox("🔊 Enable Vonnegut voice output", value=bool(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID))
        if voice_enabled:
            st.caption("💬 Type your message → Kurt responds with voice")
    
    if send_button and user_input:
        # Add user message to history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        
        # Generate Vonnegut response
        with st.spinner("Kurt is thinking..."):
            response = generate_vonnegut_response(
                user_input, 
                st.session_state.conversation_history
            )
        
        # Add response to history
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        
        # Synthesize speech if enabled
        if voice_enabled and ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID:
            with st.spinner("Generating voice..."):
                audio_data = synthesize_speech(response)
                if audio_data:
                    st.audio(audio_data, format="audio/mpeg")
        
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #CD853F; font-style: italic;">
    "So it goes." - Built with love for literature and human kindness
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()