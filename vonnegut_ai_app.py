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
    
    /* Video Background - NEGATIVE z-index puts it behind everything */
    .video-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;          /* NEGATIVE - BEHIND EVERYTHING */
        overflow: hidden;
        opacity: 0.3;
        filter: sepia(60%) hue-rotate(20deg) saturate(0.7) brightness(1.1) contrast(0.7);
        pointer-events: none;
    }
    
    /* Force all Streamlit content above video */
    .stApp > div, .main, .block-container {
        position: relative !important;
        z-index: 50 !important;    /* POSITIVE - ABOVE VIDEO */
        background: rgba(43, 27, 10, 0.1);
        font-family: 'Courier Prime', monospace;
    }
    
    /* Response boxes above video */
    .stMarkdown, .stColumns, .element-container {
        position: relative !important;
        z-index: 55 !important;    /* ABOVE VIDEO */
    }
    
    /* Input fields highest priority */
    .stTextInput {
        position: relative !important;
        z-index: 60 !important;    /* HIGHER - ABOVE EVERYTHING */
    }
    
    /* Sidebar above video */
    section[data-testid="stSidebar"] {
        position: relative !important;
        z-index: 70 !important;    /* HIGHEST - ABOVE EVERYTHING */
        background: rgba(240, 242, 246, 0.9) !important;
        backdrop-filter: blur(10px);
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
    
    # Conversation mode selector
    col_mode1, col_mode2 = st.columns([2, 3])
    
    with col_mode1:
        conversation_mode = st.selectbox(
            "Conversation mode:",
            options=["Text → Text", "Text → Audio", "Audio → Audio"],
            index=1 if (ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID) else 0
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
        # Simple voice conversation that actually works
        st.markdown("### 🎤 Voice Conversation with Kurt")
        
        # Initialize speech state
        if "speech_input" not in st.session_state:
            st.session_state.speech_input = ""
        if "speech_ready" not in st.session_state:
            st.session_state.speech_ready = False
            
        # Simple one-button speech interface
        if st.button("🎤 Click and Speak", type="primary", key="speak_now"):
            st.session_state.speech_ready = True
            st.rerun()
        
        # If ready to listen, show speech interface
        if st.session_state.speech_ready:
            st.info("🔴 **Speak now!** Your speech will automatically send to Kurt")
            
            # Simple working speech recognition
            speech_html = """
            <div style="text-align: center; margin: 20px;">
                <div id="status" style="color: #F4E8D0; font-family: 'Courier Prime'; font-size: 18px; margin-bottom: 15px;">
                    Starting microphone...
                </div>
                <button id="mic-btn" style="display: none;">🎤</button>
            </div>
            
            <script>
            // Auto-start speech recognition immediately
            if ('webkitSpeechRecognition' in window) {
                const recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                const status = document.getElementById('status');
                status.innerHTML = '🔴 LISTENING... speak now!';
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    status.innerHTML = '✅ You said: "' + transcript + '"<br>🚀 Sending to Kurt...';
                    
                    // Fill the visible text input with the result
                    setTimeout(() => {
                        const textInputs = window.parent.document.querySelectorAll('input[type="text"]');
                        for (let input of textInputs) {
                            if (input.placeholder && input.placeholder.includes('Speech will appear here')) {
                                input.value = transcript;
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                
                                // Auto-click the send button
                                setTimeout(() => {
                                    const buttons = window.parent.document.querySelectorAll('button');
                                    for (let btn of buttons) {
                                        if (btn.textContent && btn.textContent.includes('Send to Kurt')) {
                                            btn.click();
                                            break;
                                        }
                                    }
                                }, 100);
                                break;
                            }
                        }
                    }, 500);
                };
                
                recognition.onerror = function(event) {
                    status.innerHTML = '❌ Error: ' + event.error;
                };
                
                recognition.start();
            } else {
                document.getElementById('status').innerHTML = '❌ Speech recognition not supported';
            }
            </script>
            """
            
            st.components.v1.html(speech_html, height=100)
            
            # Text input that speech will fill
            user_input = st.text_input("Speech will appear here:", 
                                       value=st.session_state.speech_input,
                                       key="speech_text")
            
            # Send button that speech will auto-click
            send_button = st.button("🔊 Send to Kurt", type="primary", key="send_speech")
            
            # Handle the send
            if send_button and user_input:
                st.session_state.speech_ready = False
                st.session_state.speech_input = ""
            elif user_input != st.session_state.speech_input:
                st.session_state.speech_input = user_input
            else:
                user_input = ""
                send_button = False
        
    else:
        # Text input mode (existing functionality)
        user_input = st.text_input("Ask Kurt anything:", placeholder="What did you learn from your Dresden experience?")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            send_button = st.button("Send", type="primary")
        
        with col2:
            st.caption("💭 Kurt will respond in your selected mode")
    
    # Debug info
    if conversation_mode == "Audio → Audio":
        st.caption(f"Debug: Button clicked: {send_button}, Input: '{user_input}'")
    
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
        
        # Synthesize speech based on conversation mode
        voice_output_enabled = (conversation_mode in ["Text → Audio", "Audio → Audio"]) and ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID
        
        if voice_output_enabled:
            with st.spinner("*"):
                audio_data = synthesize_speech(response)
                
                if audio_data:
                    # Simple, magical audio display
                    st.audio(audio_data, format="audio/mpeg", start_time=0)
                    
                else:
                    st.error("❌ Voice generation failed - no audio data")
        
        # Only rerun if no voice was generated to avoid wiping audio player
        if not voice_output_enabled:
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #CD853F; font-style: italic;">
    "So it goes." - Built with love for literature and human kindness - v2.0
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()