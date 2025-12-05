# Vonnebot

**A Kurt Vonnegut Inspired Reading Companion**

Vonnebot is an AI reading companion that helps you engage with Kurt Vonnegut's work. It sees what you're reading and responds with Vonnegut's voice, wit, and Socratic teaching style.

## What It Does

- **Reading Pane** (left): Load Vonnegut texts or upload your own. The bot automatically sees what you're reading.
- **Chat** (right): Discuss passages, themes, characters—anything. Like having Vonnegut as your reading buddy.
- **Voice Avatar** (coming soon): Talk with "Kurt" through a Simli-powered avatar.

## Philosophy

Vonnebot doesn't just give answers. It asks questions back:

> "I'll tell you what I think in a moment, but first—what jumped out at you when you read that?"

This Socratic approach encourages you to develop your own interpretations rather than passively receive analysis. Vonnegut was a teacher at the Iowa Writers' Workshop—he believed learning comes from doing, not just receiving.

## Quick Start

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy from template)
cp .env.template .env
# Edit .env with your API keys

# Run the app
streamlit run vonnebot_clean.py
```

### Environment Variables

```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key (optional)
ELEVENLABS_VOICE_ID=your_voice_id (optional)
LIVEKIT_URL=your_livekit_url (for voice avatar)
LIVEKIT_API_KEY=your_livekit_key (for voice avatar)
LIVEKIT_API_SECRET=your_livekit_secret (for voice avatar)
SIMLI_API_KEY=your_simli_key (for voice avatar)
SIMLI_FACE_ID=your_simli_face_id (for voice avatar)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VONNEBOT                                  │
├────────────────────────────────┬────────────────────────────────┤
│                                │     ┌──────────────┐           │
│     📖 READING PANE            │     │   🎭 Avatar  │           │
│                                │     │   (Simli)    │           │
│     - Library texts            │     └──────────────┘           │
│     - Upload your own          │                                │
│     - Auto-context to bot      │     💬 CHAT                    │
│                                │     - Scrollable thread        │
│                                │     - Socratic engagement      │
│                                │     - Vonnegut's voice         │
└────────────────────────────────┴────────────────────────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `vonnebot_clean.py` | Main app (clean, minimal) |
| `prompts_base_prompt.txt` | Vonnegut persona + Socratic style |
| `vonnebot_agent.py` | LiveKit agent for voice avatar |
| `data/` | Corpus, excerpts, public domain texts |

## Disclaimer

Vonnebot is an AI tool trained on Kurt Vonnegut's writings to offer readers additional context and insights. It's a way to engage with his work interactively—not a literal channeling of Vonnegut himself. Born in 1922, he had his own views on technology; while we think he might have found this intriguing, we acknowledge this is just an approximation.

**This project is not affiliated with or endorsed by the Vonnegut estate.**

---

*"Listen. If this isn't nice, what is?"*
