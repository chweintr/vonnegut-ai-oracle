# Phase 2: Full RAG + Voice Integration Plan

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2024-12-13 | Replaced Simli Widget with LiveKit Web SDK | Simli widget (iframe) ignored all CSS; LiveKit gives direct video element control |
| 2024-12-13 | Added `vonnebot_agent.py` as separate service | Needed server-side agent to handle voice + RAG + Simli avatar |

---

## Architecture Evolution

### Previous Architecture (DEPRECATED)

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                             │
│  ┌─────────────┐  ┌──────────────────────────────────────┐  │
│  │ Flask       │  │ Simli Widget (iframe)                │  │
│  │ Frontend    │  │ - Hosted by Simli                    │  │
│  │             │  │ - Ignores our CSS completely         │  │
│  │             │  │ - Can't access our backend           │  │
│  │             │  │ - No RAG, no reading context         │  │
│  └─────────────┘  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Why this failed:**
1. Simli Widget is an `<iframe>` web component that renders at its own size
2. CSS transforms (`scale`, `clip-path`, `overflow:hidden`) had no effect
3. The widget's internal "Start" button was inaccessible due to cross-origin restrictions
4. The hosted Simli agent couldn't access our Flask backend, corpus, or see what text the user was reading

### Current Architecture (IMPLEMENTED 2024-12-13)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER BROWSER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │ Reading     │  │ <video>     │  │ Microphone                      │  │
│  │ Pane        │  │ element     │  │ (WebRTC audio to LiveKit)       │  │
│  │ (visible    │  │ (WE control │  │                                 │  │
│  │  passage)   │  │  the CSS!)  │  │                                 │  │
│  └──────┬──────┘  └──────▲──────┘  └────────────────┬────────────────┘  │
│         │                │                          │                    │
└─────────┼────────────────┼──────────────────────────┼────────────────────┘
          │                │                          │
          │ visible_text   │ avatar video             │ user audio
          │                │                          │
          ▼                │                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         LIVEKIT CLOUD                                    │
│                    (WebRTC infrastructure)                               │
│                           │                                              │
└───────────────────────────┼──────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAILWAY: VONNEBOT AGENT                               │
│                    (vonnebot_agent.py)                                   │
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │
│  │ Speech-to-   │   │ LLM + RAG    │   │ Text-to-     │                 │
│  │ Text         │──▶│ (GPT-4o +    │──▶│ Speech       │                 │
│  │ (Whisper)    │   │  corpus)     │   │ (ElevenLabs) │                 │
│  └──────────────┘   └──────────────┘   └──────────────┘                 │
│                            │                   │                         │
│                            │                   ▼                         │
│                     ┌──────▼──────┐   ┌──────────────┐                  │
│                     │ Corpus      │   │ Simli        │                  │
│                     │ Embeddings  │   │ (lip sync)   │                  │
│                     │ (RAG)       │   │              │                  │
│                     └─────────────┘   └──────────────┘                  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Why this works:**
1. LiveKit Web SDK gives us a raw `<video>` element we fully control
2. We can apply `border-radius: 50%`, `object-fit: cover`, exact sizing
3. Our `vonnebot_agent.py` runs server-side with full access to RAG corpus
4. Agent can receive reading context and incorporate it into responses

---

## Key Files

### Frontend (Flask + Jinja2)
- `app.py` - Flask backend with `/api/livekit-token` endpoint
- `templates/index.html` - Main UI with LiveKit Web SDK integration

### Agent (LiveKit + Simli)
- `vonnebot_agent.py` - LiveKit agent that handles voice AI + Simli avatar
- `requirements-agent.txt` - Dependencies for agent service

### Configuration
- `.env` - Environment variables (API keys, LiveKit credentials)
- `prompts_base_prompt.txt` - Vonnegut persona system prompt

### RAG Corpus
- `data/corpus_index.jsonl` - Pre-embedded corpus chunks
- `data/corpus_manifest.json` - Corpus metadata

---

## Environment Variables Required

### Flask Frontend (Railway main service)
```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
```

### Vonnebot Agent (Railway separate service)
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
SIMLI_API_KEY=...
SIMLI_FACE_ID=...
OPENAI_API_KEY=sk-...
```

---

## Connection Flow (Talk Mode)

1. User clicks "Talk" mode toggle
2. "Connect" button appears
3. User clicks "Connect"
4. Frontend calls `/api/livekit-token` to get room credentials
5. Frontend connects to LiveKit room via `LivekitClient.Room()`
6. Frontend enables microphone: `room.localParticipant.setMicrophoneEnabled(true)`
7. `vonnebot_agent.py` (running on Railway) detects new room participant
8. Agent starts Simli avatar session, publishes video track
9. Frontend receives video track, attaches to `<video id="avatarVideo">`
10. Video displays in 200px circle with proper CSS styling
11. User speaks → Agent hears via LiveKit → GPT-4o processes → Simli lip-syncs response

---

## Lessons Learned

### The Simli Widget Problem

**What we tried:**
1. CSS `transform: scale(0.5)` - Widget rendered at internal size, then scaled (blurry, wrong position)
2. `overflow: hidden` on container - Widget still rendered outside bounds
3. Proxy button to click hidden Start - Cross-origin iframe blocked access
4. CSS masks and radial gradients - Still couldn't affect iframe content

**Root cause:** Simli Widget is a web component that creates an iframe. Iframes render independently of parent CSS. There's no way to force an iframe to render at a different internal resolution.

**Solution:** Don't use the widget. Use LiveKit + Simli SDK instead, which gives us a raw video stream we can attach to our own `<video>` element.

### Why Two Services?

The Flask frontend can't run a LiveKit agent in the same process because:
1. LiveKit agents need to stay connected to rooms indefinitely
2. Flask is request/response based, not long-running
3. Agent needs different dependencies (`livekit-agents`, `livekit-plugins-simli`)

So we deploy `vonnebot_agent.py` as a separate Railway service that:
- Connects to LiveKit Cloud
- Listens for new rooms
- Joins when a user connects
- Runs the voice AI pipeline

---

## Current Status Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Text chat | ✅ Working | Fast, great UX |
| K.V.*bot signature | ✅ Working | Animated typewriter effect |
| Doodle responses | ✅ Working | SVG drawings with random triggers |
| Disclaimer | ✅ Working | Collapsible footer |
| Idle video avatar | ✅ Working | Blinking Vonnegut loop |
| LiveKit connection | ✅ Frontend ready | Needs agent deployed |
| Vonnebot agent | 🟡 Code ready | Needs Railway deployment |
| Text + Voice (Mode 2) | ✅ Backend ready | SSE streaming + TTS implemented |
| Full voice mode | 🟡 In progress | Awaiting LiveKit Cloud setup |

---

## Deployment Checklist

### 1. LiveKit Cloud Setup
- [ ] Create LiveKit Cloud project at https://cloud.livekit.io
- [ ] Get API Key and Secret
- [ ] Note the WebSocket URL (e.g., `wss://your-project.livekit.cloud`)

### 2. Simli Setup
- [ ] Get Simli API key from https://app.simli.com
- [ ] Create a face or get a face ID
- [ ] Note both values for agent env vars

### 3. Railway: Update Main Service
- [ ] Add `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` to environment

### 4. Railway: Create Agent Service
- [ ] Create new Railway service in same project
- [ ] Set root directory or Dockerfile to run `vonnebot_agent.py`
- [ ] Add all agent env vars
- [ ] Deploy

### 5. Test
- [ ] Open site, click "Talk", click "Connect"
- [ ] Check browser console for "Connected to LiveKit room"
- [ ] Check agent logs for "Vonnebot agent is now active"
- [ ] Speak and verify avatar responds

---

## Latency Considerations

### The Pipeline (each step adds latency)
1. **User speaks** → WebRTC to LiveKit (~50-100ms)
2. **Speech-to-Text** → Whisper (~200-500ms for short utterances)
3. **RAG retrieval** → Embedding + search (~100-300ms)
4. **LLM generation** → GPT-4o (~500-2000ms depending on output length)
5. **Text-to-Speech** → ElevenLabs (~200-500ms)
6. **Lip sync** → Simli (~100-200ms)
7. **Video back to user** → WebRTC (~50-100ms)

**Total realistic latency: 1.2 - 3.5 seconds**

### Optimization Strategies

| Strategy | Impact | Tradeoff |
|----------|--------|----------|
| **Shorter system prompt** | -100-300ms | Less persona depth |
| **Fewer RAG chunks** (1-2 vs 3-5) | -100-200ms | Less grounded responses |
| **Streaming TTS** | -200-400ms | More complex implementation |
| **Smaller LLM** (GPT-4o-mini) | -300-500ms | Slightly less nuanced |
| **Pre-computed embeddings** | -50-100ms | Already doing this |
| **Edge deployment** | -50-100ms | More infrastructure |

---

## Three Interaction Modes

### Mode 1: Text → Text (WORKING)
- User types question
- GPT-4o responds (~1-2 sec)
- Text appears instantly
- **Status**: Fully working, fast, great UX

### Mode 2: Text → Text + Streaming Voice (BACKEND READY)
- User types question
- GPT-4o streams response via SSE
- Text types out in real-time AS voice reads aloud
- `/api/chat-stream` and `/api/tts` endpoints implemented
- **Status**: Backend complete, frontend integration done

### Mode 3: Voice → Voice + Video (IN PROGRESS)
- User speaks to avatar
- Full voice conversation with lip-synced video
- LiveKit Web SDK integration complete in frontend
- **Status**: Needs agent deployed to Railway

---

## For Future Agents

If you're continuing this work:

1. **Don't try to fix the Simli Widget approach** - It's fundamentally broken due to iframe limitations. The LiveKit approach is correct.

2. **The agent MUST run separately** - It's a long-running process that can't live inside Flask.

3. **Check Railway logs** - If voice isn't working, check both the main service logs AND the agent service logs.

4. **LiveKit room lifecycle** - Rooms are created per-user session. The agent joins when it sees a new room. If the agent isn't running, the user will connect but see no avatar.

5. **Simli face ID** - You need a valid face ID from Simli's dashboard. The face determines the avatar appearance.

---

*"I tell you, we are here on Earth to fart around, and don't let anybody tell you different." — But how fast can we fart around? That's the latency question.*
