# Kurt Vonnegut AI Oracle

A sophisticated AI chatbot that embodies the voice, personality, and philosophy of Kurt Vonnegut Jr. (1922-2007), complete with voice synthesis using ElevenLabs.

## Features

- **Authentic Vonnegut Personality**: Based on extensive biographical research, documented quotes, and speech patterns
- **Voice Synthesis**: ElevenLabs integration for authentic Vonnegut voice
- **4 Conversation Modes**: 
  - Philosophical Discussion
  - Writing Advice  
  - War & Life Experiences
  - Social Commentary
- **Vintage Aesthetic**: Brown/orange color scheme with Courier New typography
- **Password Protection**: Access code "tralfamadore"

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   - Copy `.env.template` to `.env`
   - Add your OpenAI API key
   - Add your ElevenLabs API key and voice ID

3. **Run the Application**:
   ```bash
   streamlit run vonnegut_ai_app.py
   ```

4. **Access the App**:
   - Open your browser to the provided URL
   - Enter passcode: `tralfamadore`
   - Start conversing with Kurt Vonnegut!

## API Keys Required

- **OpenAI API Key**: For GPT-4 conversations
- **ElevenLabs API Key**: For voice synthesis (optional but recommended)
- **ElevenLabs Voice ID**: Your custom Vonnegut voice

## Authentic Vonnegut Elements

The AI incorporates:
- Signature phrases: "Listen:", "So it goes", "I tell you..."
- Biographical accuracy from extensive research
- Anti-AI-tic prompting (no "Ah," "Well," etc.)
- Midwestern conversational style
- Humanist philosophy and anti-war sentiment
- Self-deprecating humor and folksy wisdom

## Usage Tips

- Try asking about life, death, war, writing, or social issues
- Switch conversation modes in the sidebar for different perspectives
- Enable voice synthesis for the full Vonnegut experience
- Clear conversation history to start fresh topics

## Technical Notes

- Built with Streamlit for the web interface
- Uses GPT-4 with comprehensive personality prompting
- ElevenLabs API for high-quality voice synthesis
- Responsive design with custom CSS styling

*"If this isn't nice, what is?"* - Kurt Vonnegut