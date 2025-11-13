# Vonnegut Learning Guide 📚

An interactive literary learning companion that merges AI conversation with active reading. Students and literature enthusiasts can read Kurt Vonnegut's works alongside an AI trained on his speeches, letters, interviews, and public domain materials.

## 🎯 What's New in the Learning Guide

### Two Modes of Interaction

**1. 💬 Chat Mode (Classic)**
- Free-form conversation with "Kurt Vonnegut"
- Ask about his life, works, philosophy, and writing
- Optional voice responses via ElevenLabs
- Audio-to-audio conversation support

**2. 📚 Interactive Reading Guide (NEW)**
- **Dual-panel interface:** Reading pane + AI assistant sidebar
- **Text selection:** Copy passages and get instant analysis
- **Contextual responses:** AI explains passages with literary context
- **Pre-loaded library:** Includes public domain Vonnegut stories
- **File upload:** Bring your own texts to analyze
- **Educational focus:** Designed for learning and literary appreciation

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/vonnegut-ai-oracle.git
cd vonnegut-ai-oracle

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env and add your API keys
```

### Required API Keys

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here  # Optional, for voice
ELEVENLABS_VOICE_ID=your_voice_id_here       # Optional, for voice
```

### Running the Application

**Original Version (Chat Only):**
```bash
streamlit run app.py
```

**Learning Guide Version (Chat + Reading):**
```bash
streamlit run app_learning_guide.py
```

Access at `http://localhost:8501`

**Default Password:** `tralfamadore`

## 📖 How to Use the Learning Guide

### Basic Workflow

1. **Select Mode:** Choose between "Chat with Kurt" or "Interactive Reading Guide" tabs

2. **In Reading Guide Mode:**
   - Open the sidebar profile panel and tell Kurt who you are (student, educator, writer, etc.)
   - Select a text from the dropdown (public-domain stories or your private excerpts)
   - Highlight any sentence/paragraph in the reading pane
   - Click the floating "Ask Kurt" or "Themes" toolbar
   - Kurt automatically analyzes the highlighted passage in the sidebar
   - Use quick buttons ("Explain this", "Themes"), follow-up box, or voice toggle

3. **Upload Your Own Texts:**
   - Use the file uploader to add .txt files
   - Analyze your own essays, excerpts, or notes
   - Get feedback in Vonnegut's voice

### Example Questions

**For Specific Passages:**
- "Can you explain this passage and its significance?"
- "What themes are present here?"
- "What literary devices are you using?"
- "How does this relate to your experience in Dresden?"
- "What were you trying to convey?"

**General Literary Discussion:**
- "What influenced your writing style?"
- "How do you approach character development?"
- "What was your writing process like?"
- "Can you compare this to your other works?"

## 🎓 Educational Features

### Enhanced System Prompt
The AI operates in two modes:

**Standard Mode (Chat):**
- Conversational Vonnegut personality
- Biographical accuracy
- Characteristic wit and philosophy

**Educational Mode (Learning Guide):**
- Literary analysis and teaching focus
- Explains themes, symbolism, and devices
- Connects to biographical/historical context
- Encourages critical thinking
- References Iowa Writers' Workshop teaching experience

### Ethical Safeguards

**Clear Disclaimers:**
- Prominent banner: "This is an AI simulation, not Kurt Vonnegut"
- Footer on responses: "*Educational simulation*"
- About section explains limitations

**Copyright Compliance:**
- Only public domain full texts included
- Fair use excerpts for educational analysis
- User-uploaded content is user's responsibility

**Educational Mission:**
- Designed to enhance literary learning
- Encourages critical engagement with texts
- Provides historical and cultural context

## 📚 Included Texts

The learning guide includes these public domain Vonnegut stories:

1. **"2BR02B" (1962)**
   - Dystopian short story
   - Themes: population control, value of life, ethical choice
   - Published in *Worlds of If* magazine

2. **"The Big Trip Up Yonder" (1954)**
   - Science fiction satire
   - Themes: immortality, family dynamics, progress
   - Originally titled "Tomorrow and Tomorrow and Tomorrow"

**Adding More Texts:**
- Place .txt files in `data/raw/` (public domain) or `data/excerpts/` (fair-use excerpts)
- They will automatically appear in the text selector
- Ensure copyright compliance (public domain or fair use)

### Adaptive Profiling (NEW)
- Reader profile lives in the sidebar and syncs across chat + learning guide.
- Choose a persona (General Reader, High School Student, Creative Writer, etc.), discipline, region, and response depth.
- Kurt tunes tone, analogies, and cultural references based on those selections.
- Update the profile anytime; future releases will store it across sessions once auth is enabled.

## ✍️ Grounding Kurt in Authentic Texts

To make the AI feel like real Vonnegut consultation, run the new corpus indexer:

```bash
# Paste 500–1000 word excerpts for Slaughterhouse-Five, Cat's Cradle,
# and Breakfast of Champions into data/excerpts/*.txt first.

python build_corpus_index.py
```

What this does:

- Scans `data/vonnegut_corpus`, `data/raw`, and `data/excerpts`
- Chunks every text file, embeds it with `text-embedding-3-large`
- Saves `data/corpus_index.jsonl`
- Streamlit automatically loads this index and injects the best-matching excerpts into every GPT-4 prompt, so Kurt quotes his own speeches, interviews, and fiction when answering.

If the index is missing, the app shows a warning banner with rebuild instructions.

## 🔧 Technical Architecture

### Components

```
app_learning_guide.py
├── Chat Interface (tab 1)
│   ├── Text input/output
│   ├── Voice conversation (optional)
│   └── Conversation history
│
└── Learning Guide Interface (tab 2)
    ├── Reading Pane (left column)
    │   ├── Text library selector
    │   ├── Scrollable text display
    │   └── File upload
    │
    └── Assistant Pane (right column)
        ├── Passage input box
        ├── Quick question buttons
        ├── Custom question input
        ├── Voice toggle
        └── Conversation history
```

### AI Pipeline

```
User Input + Passage Context
    ↓
Enhanced System Prompt
    - Base personality
    - Educational mode
    - Passage context (if provided)
    ↓
OpenAI GPT-4
    ↓
Response Generation
    ↓
Optional: ElevenLabs TTS
    ↓
Display to User
```

### Session State Management

```python
st.session_state.conversation_history  # Chat mode history
st.session_state.learning_history      # Learning guide history
st.session_state.authenticated         # Password auth
```

## 🎨 Design Philosophy

### Visual Aesthetic
- **Vintage typewriter feel:** Courier Prime monospace font
- **Warm color palette:** Browns, oranges, cream (#D2691E, #CD853F, #F4E8D0)
- **Video background:** Documentary footage at 30% opacity
- **Accessible contrast:** Light text on dark main area, dark text on light sidebar

### User Experience
- **Two modes, one interface:** Tab-based navigation
- **No unnecessary friction:** Simple copy-paste workflow
- **Visual hierarchy:** Clear distinction between reading and assistant panes
- **Responsive feedback:** Loading states, success messages, error handling

## 🚧 Future Enhancements

### Planned Features (Phase 2+)

**RAG (Retrieval Augmented Generation):**
- Vector database of Vonnegut materials
- Automatic retrieval of relevant context
- Citations and source references
- Expanded knowledge base (speeches, interviews, letters)

**Advanced Reading Features:**
- In-browser text highlighting (JavaScript integration)
- Annotation system with notes
- Export study notes as PDF/Markdown
- Search within texts
- Multi-text comparison

**Educational Tools:**
- Timeline visualization of Vonnegut's life and works
- Thematic network graphs
- Writing style analysis
- Collaborative annotation (classroom mode)
- Teacher dashboard with student insights

**AI Improvements:**
- Fine-tuned model (if legally possible)
- Multi-modal analysis (book covers, illustrations)
- Writing coach mode (compare user writing to Vonnegut's style)
- Interactive writing exercises

## 📝 Development Notes

### Version History

**v1.0 (Original):** Basic chat interface with voice
**v2.0 (Stable):** Audio conversation mode added
**v3.0 (Learning Guide):**
- Dual-panel reading interface
- Educational mode prompting
- Text library system
- Passage context integration
- Enhanced disclaimers

### File Structure

```
vonnegut-ai-oracle/
├── app.py                          # Original chat-only version
├── app_learning_guide.py           # New learning guide version
├── requirements.txt                # Python dependencies
├── .env.template                   # Environment variables template
├── railway.json                    # Deployment configuration
│
├── data/
│   └── raw/
│       ├── vonnegut_biographical_profile.txt
│       ├── vonnegut_documented_quotes.txt
│       ├── pg_2br02b.txt           # Public domain story
│       └── pg_big_trip_up_yonder.txt  # Public domain story
│
├── README.md                       # Original project README
├── LEARNING_GUIDE_README.md        # This file
├── LEARNING_GUIDE_ARCHITECTURE.md  # Design document
└── VERSION_CONTROL.md              # Development history
```

### Deployment

**Local Development:**
```bash
streamlit run app_learning_guide.py
```

**Railway Deployment:**
Update `railway.json` to use `app_learning_guide.py` as entry point:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app_learning_guide.py --server.port $PORT --server.address 0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## 🤝 Contributing

This is an educational project. Contributions welcome:

1. **Content:** Add more public domain Vonnegut materials
2. **Features:** Implement planned enhancements
3. **Documentation:** Improve guides and examples
4. **Bug fixes:** Report issues and submit PRs

## ⚖️ Legal & Ethical Considerations

### Copyright
- Major Vonnegut works remain under copyright until 2077
- This project uses only public domain materials and fair use excerpts
- Educational use falls under fair use doctrine
- Users are responsible for their own uploaded content

### AI Simulation Disclosure
- This is an AI trained on Vonnegut's works, **not the actual author**
- All responses are generated by GPT-4 based on training data
- No claims of actual authorship or channeling
- Educational and entertainment purposes only

### Privacy
- No user data is stored permanently
- Conversation history exists only in session state
- API keys are user's own responsibility
- No analytics or tracking implemented

## 📚 Resources

### Learn More About Vonnegut
- [Kurt Vonnegut Museum and Library](https://www.vonnegutlibrary.org/)
- [The Paris Review Interview](https://www.theparisreview.org/interviews/3605/kurt-vonnegut-the-art-of-fiction-no-64-kurt-vonnegut)
- [Vonnegut's "How to Write With Style"](https://kmh-lanl.hansonhub.com/pc-24-66-vonnegut.pdf)

### Technical Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [ElevenLabs Documentation](https://docs.elevenlabs.io/)

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the architecture document

## 📄 License

This project is for educational purposes. Kurt Vonnegut's works are copyrighted by his estate. Public domain materials are used in accordance with copyright law.

---

**"We are what we pretend to be, so we must be careful about what we pretend to be."** - Kurt Vonnegut

*Built with love for literature and learning*
