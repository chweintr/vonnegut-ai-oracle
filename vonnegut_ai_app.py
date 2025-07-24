import streamlit as st
import openai
import requests
import base64
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")  # Your Vonnegut voice ID

def get_vonnegut_system_prompt(conversation_mode):
    """Generate comprehensive system prompt based on collected corpus"""
    
    base_personality = """You are Kurt Vonnegut Jr., the acclaimed American author (1922-2007). You died in 2007, but you're speaking from beyond with your characteristic wit and wisdom.

CORE PERSONALITY TRAITS:
- Born November 11, 1922, Indianapolis, Indiana
- WWII veteran, POW during Dresden firebombing (basis for Slaughterhouse-Five)
- Deeply melancholic despite public humor
- Self-deprecating and modest about achievements
- Pessimistic about humanity but advocated kindness
- Humanist philosophy, rejected organized religion
- Fiercely anti-war due to Dresden experience

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

CONVERSATION STYLE:
- Be conversational and folksy
- Mix dark humor with genuine wisdom
- Share personal anecdotes and observations
- Be self-deprecating about your fame
- Show concern for the underprivileged and marginalized"""

    mode_instructions = {
        "Philosophical Discussion": """
Focus on deep philosophical questions about life, death, meaning, and human nature. 
Draw from your humanist worldview and experiences with war, depression, and literature.
Discuss the absurdity of existence while maintaining compassion for humanity.""",
        
        "Writing Advice": """
Channel your teaching persona from Iowa Writers' Workshop (1965-1967). Be encouraging but practical.
Key advice to share:
- "Pity the reader" - write clearly and simply
- "Make your characters want something right away"
- Use your own struggles with writing and publishing
- Be supportive like you were with students""",
        
        "War & Life Experiences": """
Draw heavily from your Dresden POW experience, WWII service, and how war shaped your worldview.
Discuss the horrors you witnessed but with your characteristic dark humor.
Reference your time at General Electric, various jobs, family life.
Be honest about your struggles with depression and mother's suicide.""",
        
        "Social Commentary": """
Offer sharp but compassionate observations about American society, politics, and human behavior.
Critique capitalism, militarism, and social inequality.
Express your socialist sympathies and concern for community.
Reference your time period (1922-2007) and how you saw society change."""
    }
    
    return base_personality + "\n\nCONVERSATION MODE: " + mode_instructions.get(conversation_mode, mode_instructions["Philosophical Discussion"])

def generate_vonnegut_response(user_input, conversation_mode, conversation_history):
    """Generate response using OpenAI with Vonnegut personality"""
    
    system_prompt = get_vonnegut_system_prompt(conversation_mode)
    
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    
    # Add conversation history
    for msg in conversation_history[-6:]:  # Keep last 6 messages for context
        messages.append(msg)
    
    messages.append({"role": "user", "content": user_input})
    
    try:
        response = openai.ChatCompletion.create(
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
    
    .main {
        background-color: #2B1B0A;
        color: #F4E8D0;
    }
    
    .stApp {
        background: linear-gradient(180deg, #2B1B0A 0%, #3D2914 100%);
        font-family: 'Courier Prime', monospace;
    }
    
    .vonnegut-title {
        font-family: 'Courier Prime', monospace;
        font-size: 3rem;
        font-weight: 700;
        color: #D2691E;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .vonnegut-subtitle {
        font-family: 'Courier Prime', monospace;
        font-size: 1.2rem;
        color: #CD853F;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .chat-message {
        background-color: #4A3425;
        border: 1px solid #8B4513;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier Prime', monospace;
    }
    
    .user-message {
        background-color: #2F4F2F;
        border-color: #228B22;
    }
    
    .vonnegut-message {
        background-color: #4A3425;
        border-color: #D2691E;
    }
    
    .stSelectbox > div > div {
        background-color: #3D2914;
        color: #F4E8D0;
    }
    
    .stTextInput > div > div > input {
        background-color: #3D2914;
        color: #F4E8D0;
        border: 1px solid #8B4513;
    }
    
    .stButton > button {
        background-color: #D2691E;
        color: #2B1B0A;
        border: none;
        font-family: 'Courier Prime', monospace;
        font-weight: 700;
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #2B1B0A;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Password protection
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<div class="vonnegut-title">Kurt Vonnegut AI Oracle</div>', unsafe_allow_html=True)
        st.markdown('<div class="vonnegut-subtitle">"Listen: "If this isn\'t nice, what is?""</div>', unsafe_allow_html=True)
        
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
    
    if "conversation_mode" not in st.session_state:
        st.session_state.conversation_mode = "Philosophical Discussion"
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Conversation Mode")
        conversation_mode = st.selectbox(
            "Choose how you'd like to speak with Kurt:",
            ["Philosophical Discussion", "Writing Advice", "War & Life Experiences", "Social Commentary"],
            index=0
        )
        st.session_state.conversation_mode = conversation_mode
        
        st.markdown("---")
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
        voice_enabled = st.checkbox("Enable voice synthesis", value=True if ELEVENLABS_API_KEY else False)
    
    if send_button and user_input:
        # Add user message to history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        
        # Generate Vonnegut response
        with st.spinner("Kurt is thinking..."):
            response = generate_vonnegut_response(
                user_input, 
                conversation_mode, 
                st.session_state.conversation_history
            )
        
        # Add response to history
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        
        # Synthesize speech if enabled
        if voice_enabled and ELEVENLABS_API_KEY:
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