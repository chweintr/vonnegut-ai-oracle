# Vonnebot
"A reader's desk that talks back in Vonnegut's voice."

## Vision
Vonnebot is a reading companion for people who want to feel a writer's mind at work, not just skim plot summaries. You read Vonnegut, and it reads with you, answering questions in a voice shaped by his essays, interviews, and fiction. The goal is intimacy with the text, not automation of analysis.

It exists because most study guides flatten literature into bullet points. Vonnegut's writing is personal, moral, funny, and a little dangerous; it deserves a guide that can meet that energy. Vonnebot makes the act of reading interactive and reflective, so your own interpretation is the center of gravity.

What makes it different is the grounding: replies are anchored in Vonnegut's actual words and a Socratic posture that keeps turning the question back toward you. It's less "AI summary," more "workshop conversation."

## Platform Context
Vonnebot is the first "Vonneguides" experiment: a pattern for building author-specific reading companions that honor voice, context, and craft. The long-term vision is a small family of guides for other authors and classrooms, all using the same grounded retrieval + tutoring pipeline.

## Categories / Organization
| Category | What It Covers | Who It's For |
| --- | --- | --- |
| Reading Experience | The split-pane reader, highlights, and context capture | Anyone actively reading a text |
| Companion Voice | Vonnegut persona, tone, and Socratic questioning | Readers who want dialogue, not answers |
| Grounded Sources | Corpus excerpts, interviews, essays, citations | Students, educators, researchers |
| Modes | Text chat now; voice/avatar later | Readers who prefer conversation |

## Current State
| Area | Status | Notes |
| --- | --- | --- |
| Split-pane reading + chat | ✅ Active | Reads what you're reading in real time |
| Grounded RAG answers | ✅ Active | Uses corpus excerpts to steer responses |
| Persona + Socratic flow | ✅ Active | Questions are part of the answer |
| Voice avatar | 📋 Planned | LiveKit/Simli integration in progress |
| Persistent learner profiles | 📋 Planned | Session-first today |

## Roadmap / Planned
- Voice-first mode with the Vonnegut avatar
- Richer learner profiles (discipline, region, reading goals)
- Ambient context capture (no highlight required)
- Multi-author "Vonneguides" expansion

## How It Works
1. You load a text and start reading.
2. The reader captures the passage you're focused on.
3. You ask a question or click a prompt.
4. The system pulls relevant Vonnegut sources and responds in character.
5. The reply invites you to interpret, connect, or disagree.

## Aesthetic / Vibe
Wry, humane, and slightly irreverent. It should feel like a paper-laden desk, a late-night workshop, and a friend who reads with a pencil in hand. The tone is curious and direct, with a dry wit that keeps the conversation honest.

---
# Technical Documentation
---

## Vonnebot

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
# Force redeploy Tue Dec 16 11:00:40 EST 2025
