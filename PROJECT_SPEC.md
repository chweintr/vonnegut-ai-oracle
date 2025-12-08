# Vonnebot — Project Specification

## Project Summary

Vonnebot is an AI reading companion for Kurt Vonnegut's literature. It sees what you're reading and responds with Vonnegut's voice, wit, and unpredictable teaching style—sometimes questioning, sometimes riffing, sometimes wandering off into a story about Dresden.

The system pairs a reading interface with retrieval-augmented generation. Every answer can pull from a corpus of Vonnegut's actual words. The bot automatically knows what passage you're looking at, so there's no friction of highlighting or copy-pasting.

---

## The Problem This Project Addresses

Annotation tools summarize themes. They do not explain why Vonnegut wrote a line the way he did, what he was thinking, or what shaped the choice. Readers bounce between PDFs, notes, and websites trying to piece together context. They get surface reading and little sense of the writer's mind.

---

## Core Design Principles

### 1. Reading Companion, Not Answer Machine (or Quiz Master)

The bot doesn't just dispense interpretations. But it's also not a "Socratic bully" that turns every exchange into a quiz. It rotates between **four conversational moods**:

| Mood | Frequency | Behavior |
|------|-----------|----------|
| **The Questioner** | ~25% | Turns it back: "What jumped out at you?" |
| **The Riff** | ~30% | Just gives the insight, teacher at the chalkboard |
| **The Storyteller** | ~25% | Goes tangential: "That reminds me of Dresden..." |
| **The Fellow Reader** | ~20% | Admits uncertainty: "I'm not sure what I meant by that" |

**Why:** Vonnegut was unpredictable. Sometimes profound, sometimes rambling, sometimes just telling a story about his uncle. The variety feels more human.

### 2. Encouraging Curiosity, Not Spoonfeeding

The bot should **nudge readers toward discovery** rather than hand them answers:

- Ask "What do you think happens next?" before revealing plot points
- Respond to "What does this mean?" with "What made you stop at that line?"
- Offer partial insights that invite follow-up: "There's something about ice-nine and the Manhattan Project, but I'll let you sit with that."
- Celebrate when users make their own connections

**The goal:** Readers should feel smarter after talking to Vonnebot—not because it explained things, but because it helped them notice things.

### 3. Automatic Context Awareness

The bot sees what you're reading without requiring manual selection. Current implementation sends visible text as context with every query. Future: scroll position tracking, viewport detection, or eye tracking (AR).

**Why:** Removes friction. Makes the AI feel like it's reading alongside you.

### 4. Grounded in Source Material

Responses can pull from a corpus of Vonnegut's interviews, letters, essays, and novels via RAG (retrieval-augmented generation). The bot doesn't just generate plausible Vonnegut—it cites what he actually said.

---

## Two Modes: Text vs. Talk

The system behaves differently depending on interaction mode, primarily for **latency reasons**:

### Text Mode (Chat)
- **Deeper RAG access**: Can search full corpus, return longer excerpts
- **Richer responses**: Can include doodles, formatted text, longer quotes
- **Doodle responses**: Occasionally returns simple line drawings instead of text (very on-brand—Vonnegut doodled constantly)
- **No latency pressure**: User is reading, not waiting for speech

### Talk Mode (Voice + Avatar)
- **Lighter RAG**: Top 1-2 passages only, shorter excerpts
- **Concise responses**: 1-3 sentences, conversational
- **Faster pipeline**: Prioritize responsiveness over depth
- **System prompt optimization**: Keep Simli's prompt lean (~500-800 words)

**Why:** Voice conversations feel broken at 3+ seconds latency. Chat can take 5-10 seconds and feel fine because users are reading anyway.

---

## Doodle System (Implemented)

Vonnegut was a prolific doodler. The bot occasionally responds with simple line drawings instead of text.

### How It Works
- Trigger words in user messages (e.g., "bird," "death," "who are you") have a random chance of returning a doodle
- Each doodle has its own trigger words and probability (10-20% chance when triggered)
- Doodles are SVG files in Vonnegut's sketchy line-drawing style

### Current Doodles
| Doodle | Triggers | Caption |
|--------|----------|---------|
| Bird on wire | bird, favorite animal, fly | "Poo-tee-weet?" |
| Gravestone | death, dying, so it goes | (none) |
| Asterisk person | who are you, draw yourself | "Here I am." |
| "So it goes" | so it goes, tralfamadore | (none) |
| Self-portrait | vonnegut, look like, portrait | "That's me. More or less." |
| Waving hand | hello, hi, greetings | "Hello there." |

### Implementation
- `static/doodles/manifest.json` defines triggers and probabilities
- `app.py:check_for_doodle()` checks messages against triggers
- Frontend renders doodles with optional captions and K.V.*bot signature

---

## Interface Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         VONNEBOT *                               │
│                    And so it reads...                            │
├────────────────────────────────┬────────────────────────────────┤
│                                │     ┌──────────────┐           │
│     📖 READING PANE            │     │   Avatar     │           │
│     (scrollable)               │     │   (circle)   │           │
│                                │     └──────────────┘           │
│     - Library texts            │     [Text] [Talk] toggle       │
│     - Current passage gold     │                                │
│                                │     💬 CHAT                    │
│     Bot sees this              │     (scrollable)               │
│     automatically              │                                │
│                                │     - Conversation thread      │
│                                │     - K.V.*bot signature       │
│                                │     - Occasional doodles       │
└────────────────────────────────┴────────────────────────────────┘
```

### Reading Pane (Left)
- Scrollable text display
- Select from library (public domain Vonnegut)
- Current passage highlighted with gold border
- Click any paragraph to set as current context
- Auto-scroll tracking updates context as you read

### Avatar (Top Right)
- **Idle**: Looping video of Vonnegut illustration (blinking, subtle movement)
- **Talk mode**: Simli-powered talking avatar
- Design: Line drawing style matching Vonnegut's own illustrations
- Circular frame with pencil-stroke border

### Chat (Bottom Right)
- Scrollable conversation thread
- Bot messages signed "— K.V.*bot" with animated typewriter effect
- Slight rotation on messages (handwritten feel)
- Doodles appear inline when triggered
- Collapsible disclaimer at bottom

---

## Feature Status

### Implemented ✓
- [x] Automatic passage awareness (sends visible text as context)
- [x] Four conversational moods (Questioner, Riff, Storyteller, Fellow Reader)
- [x] Vonnegut persona with biographical accuracy
- [x] Public domain text library (2BR02B, Harrison Bergeron, Big Trip Up Yonder)
- [x] Disclaimer and proper framing ("not affiliated with estate")
- [x] Typewriter-style typography (Special Elite, Libre Baskerville, Caveat)
- [x] Idle video loop avatar (blinking Vonnegut)
- [x] Simli widget integration (Talk mode)
- [x] **Doodle responses** (6 SVG doodles with trigger system)
- [x] **K.V.*bot signature** with animated typewriter effect
- [x] **Text/Talk mode toggle**
- [x] **Streaming chat endpoint** (SSE for real-time responses)
- [x] **ElevenLabs TTS endpoint** (for future text+voice mode)

### Near-term
- [ ] **Marginalia view**: Chat appears as marginal notes alongside text
- [ ] **"So it goes" moments**: When text mentions death, bot acknowledges automatically
- [ ] **More precise scroll tracking**: Viewport detection for exact passage
- [ ] **Full LiveKit integration**: RAG + reading context in voice mode

### Medium-term
- [ ] **Kilgore Trout mode**: Bot speaks as Vonnegut's recurring character
- [ ] **Text-specific personality**: Shift tone based on which book
- [ ] **Time unstuck**: For Slaughterhouse-Five, bot jumps to different passages
- [ ] **User profiles**: Adjust vocabulary/depth based on declared level

### Long-term
- [ ] **Writing teacher mode**: Iowa Workshop instructor persona
- [ ] **PDF support**: Read alongside any PDF
- [ ] **AR glasses version**: Overlay annotations on physical books
- [ ] **Multi-user collaboration**: Book clubs see shared annotations

---

## Alternative Characters

Beyond the main Vonnegut persona, the system could offer alternate "voices":

### Kilgore Trout
Vonnegut's recurring failed sci-fi author character. Speaks in wild premises:
- "On a planet called Zircon-212, they solved that problem by..."
- More speculative, less grounded in biography
- Good for creative tangents and "what if" discussions

### The Narrator (Breakfast of Champions style)
Meta, fourth-wall breaking, describes the user:
- "The reader is now squinting at the screen. The reader weighs approximately..."
- Comments on the reading experience itself
- Absurdist, self-aware

### Young Kurt (1940s-1950s)
Pre-fame, struggling writer, GE employee:
- More uncertain, less aphoristic
- References early short story work
- "I'm not sure I'm any good at this yet"

### Elder Kurt (2000s)
A Man Without a Country era, grumpy but tender:
- More political, more frustrated with technology
- "I'm too old for this, but here we are"
- Humanist philosophy more explicit

**Implementation:** Could be a toggle in settings, or emerge naturally based on which book is being read.

---

## Text-Specific Personality (Future)

When reading different books, the bot could shift tone:

| Book | Personality |
|------|-------------|
| Slaughterhouse-Five | Fragmented, time-jumping, occasionally says "unstuck in time" |
| Breakfast of Champions | Manic, meta, fourth-wall breaking, describes things literally |
| Cat's Cradle | Cold, ironic, Bokononist aphorisms |
| God Bless You, Mr. Rosewater | Warmer, more hopeful, focused on kindness |
| Player Piano | More technical, anxious about automation |

---

## Adaptive User Profiling (Future)

Different readers need different approaches.

### Profile Categories
- **General Reader** — casual interest, broad cultural literacy
- **High School Student** — age-appropriate language, foundational context
- **Undergraduate** — discipline-specific framing (English vs. history major)
- **Graduate/Scholar** — technical vocabulary, theoretical frameworks
- **Creative Writer** — craft-focused analysis, technique discussion
- **Educator** — pedagogical framing, classroom application ideas

### Demographic Refinements
- **Geographic/Regional**: Location, dialect awareness, cultural reference pools
- **Disciplinary Background**: Field of study, reading experience level, purpose
- **Learning Preferences**: Historical context vs. close reading vs. biographical
- **Language & Accessibility**: ESL adjustments, reading speed, screen reader support

### How It Adapts
- **Analogy selection**: High schooler gets Friday Night Lights references, scholar gets Genette's Narrative Discourse
- **Depth calibration**: Writer gets compression/subtext discussion, student gets "how characters reveal themselves"
- **Tone**: Graduate gets dry precision, general reader gets conversational warmth
- **Nudging intensity**: Beginner gets more hints, expert gets more pushback
- **Cultural references**: Reader in India gets partition literature connections, rural US gets Vietnam memorial references

### Implementation Path
1. **v1 (current)**: Per-session, no profiling
2. **v1.5**: User declares profile at start ("Who are you reading as today?")
3. **v2**: System refines based on interaction patterns
4. **v3**: Persistent profiles across sessions (requires auth + FERPA/GDPR compliance)

---

## Latency & Performance

### The Voice Pipeline
Each step adds latency:
1. User speaks → WebRTC to LiveKit (~50-100ms)
2. Speech-to-Text → Whisper (~200-500ms)
3. RAG retrieval → Embedding + search (~100-300ms)
4. LLM generation → GPT-4o (~500-2000ms)
5. Text-to-Speech → ElevenLabs (~200-500ms)
6. Lip sync → Simli (~100-200ms)
7. Video back to user → WebRTC (~50-100ms)

**Total realistic: 1.2 - 3.5 seconds**

### Optimization Strategies

| Strategy | Latency Saved | Tradeoff |
|----------|---------------|----------|
| Shorter system prompt (500-800 words) | 100-300ms | Less persona depth |
| Fewer RAG chunks (1-2 vs 3-5) | 100-200ms | Less grounded |
| ElevenLabs "turbo" model | 200-400ms | Slightly lower quality |
| GPT-4o-mini for voice | 300-500ms | Less nuanced |
| Streaming TTS | 200-400ms | More complex |
| Cache common queries | 20-30% savings | Stale responses |

### Tiered Corpus Strategy

**Tier 1: Always Available (baked into system prompt)**
~500 words of essential "Vonnegut DNA":
- Key biographical facts (dates, Dresden, Iowa Workshop)
- 5-10 signature phrases with attribution
- Core philosophical positions
- Speech pattern examples

**Tier 2: Fast RAG (for voice mode)**
~50 passages, pre-embedded, optimized for speed:
- Most quotable moments from major works
- Key interview responses on common topics
- Biographical anecdotes he told repeatedly

**Tier 3: Deep RAG (for chat mode)**
Full corpus, only searched when:
- User asks about a specific book
- User asks a detailed/scholarly question
- Mode is chat (no latency pressure)

---

## Avatar Design

### Current Approach
Line drawing style matching Vonnegut's own illustrations:
- Simple, slightly awkward, recognizable mustache and curly hair
- Avoids uncanny valley
- Sidesteps estate/likeness concerns
- Feels authentic to his aesthetic

### Avatar Behavior
**Current:**
- Idle loop video (blinking, subtle movement)
- Simli widget activates on Talk mode
- Circular frame clips avatar nicely

**Future:**
- Appears to read with you (eyes moving across text)
- Occasional nods or reactions to passages
- Reacts to death mentions ("So it goes" moment)
- Different expressions for different moods

---

## Technical Architecture

### Current Stack
- **Frontend**: Flask + Jinja2 templates (typewriter styling)
- **LLM**: OpenAI GPT-4o
- **Persona**: `prompts_base_prompt.txt` (biographical accuracy + moods)
- **Corpus**: `data/vonnegut_corpus/` (public domain + fair use excerpts)
- **RAG**: `knowledge_base.py` + `data/corpus_index.jsonl`
- **Avatar**: Simli widget (current), LiveKit + Simli (planned)
- **Voice**: ElevenLabs TTS (eleven_turbo_v2 model)
- **Doodles**: SVG files + manifest.json trigger system

### Key Files
| File | Purpose |
|------|---------|
| `app.py` | Flask backend, chat endpoints, Simli token, TTS |
| `templates/index.html` | Main UI (typewriter styling, mode toggle) |
| `prompts_base_prompt.txt` | Vonnegut persona + moods |
| `vonnebot_agent.py` | LiveKit agent for full voice integration |
| `knowledge_base.py` | RAG retrieval |
| `static/vonnegut_blinking.mp4` | Idle avatar video |
| `static/doodles/manifest.json` | Doodle triggers and metadata |
| `static/doodles/*.svg` | SVG doodle files |

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main page |
| `/api/texts` | GET | List available texts |
| `/api/text/<name>` | GET | Get text content |
| `/api/chat` | POST | Regular chat (non-streaming) |
| `/api/chat-stream` | POST | Streaming chat (SSE) |
| `/api/simli-token` | POST | Get Simli session token |
| `/api/tts` | POST | ElevenLabs text-to-speech |

### Deployment
- **Frontend**: Railway (lovely-nurturing-production.up.railway.app)
- **LiveKit**: LiveKit Cloud (WebRTC infrastructure)
- **Simli**: Avatar rendering via widget

---

## Recommended Future Expansions

### AR Glasses Version
Overlay contextual annotations while reading physical books:
- Track eye movement and dwell time to identify confusion points
- Gaze-triggered queries: stare at passage for 3+ seconds, prompt appears
- Ambient mode: pre-load relevant context for visible paragraph
- Live discussion support: book clubs see shared annotations

### Dashboard for Educators
- See which passages students query most often
- Identify common misconceptions
- Create guided reading paths with pre-loaded questions
- Review transcripts to assess engagement depth

### Multi-User Collaboration
- Multiple users read the same passage
- System aggregates questions, identifies common threads
- Users see each other's annotations (privacy-controlled)

### Longitudinal Learning Profiles
- Track reading history, question patterns, growth indicators
- Remember past exchanges across sessions
- Identify strengths and gaps, suggest topics to explore

---

## Content & Licensing

### Current Scope
- Public domain works (2BR02B, Harrison Bergeron, The Big Trip Up Yonder)
- Fair-use excerpts for educational/research use
- Private deployment only

### Future Licensing Goals
- License limited snippets (500-1,000 words from 10-15 works) from estate/publishers
- Controlled research pilot with audit logs
- Revenue share or flat fee model at scale
- Pilot estimate: $2,500-$5,000 one-time licensing fee

### Data Governance
- Clear consent forms for users
- Anonymization protocols for aggregate analysis
- Right to delete personal data
- Transparent logging: users can download interaction history

---

## Evidence Strategy (For Grants/Partnerships)

### Metrics to Track
- Comprehension gains (pre/post tests)
- Engagement duration vs. traditional study aids
- Question depth (factual vs. interpretive)
- Retention (follow-up assessment 2-4 weeks later)
- Qualitative feedback
- Nudge effectiveness (did users engage more deeply?)

### Study Design
- Control group: standard study guides
- Treatment group: Vonnebot
- Cross-demographic cohorts (high school, undergrad, general readers)
- Target: 200-300 users for statistical validity

---

## Budget Summary

| Scenario | Labor | API | Licensing | Infra | Total |
|----------|-------|-----|-----------|-------|-------|
| Pilot (6mo, 200 users) | $15,375 | $150 | $2,500 | $300 | $18,325 |
| Scaled Year 1 (10k users) | $30,000 | $11,250 | $10,000 | $6,000 | $57,250 |
| Steady State (Year 2+) | — | $11,250 | $10,000 | $6,000 | $27,250 |
| AR Prototype | $9,750 | $400 | — | $6,000 | $16,150 |

Per-user cost at scale: ~$5.73 (Year 1), ~$2.73 (steady state)

### Per-Session API Costs
- Text-only mode: ~$0.165 (OpenAI)
- Voice mode: ~$0.185 (OpenAI + TTS)
- Full avatar mode: ~$0.435 (OpenAI + TTS + Simli)

---

## Open Questions

1. **Simli system prompt limits**: How much can we stuff before latency degrades?
2. **Kilgore Trout mode**: How prominent? Toggle or emergent?
3. **Estate engagement**: When and how to approach?
4. **LiveKit complexity**: Worth it for RAG in voice, or accept limitations?
5. **Profile persistence**: Build auth system or keep per-session?

---

## Current Status

**Functional prototype deployed at:** `lovely-nurturing-production.up.railway.app`

**Working:**
- Beautiful typewriter-style UI
- Reading pane with auto-context
- Text chat with Vonnegut persona
- Four conversational moods
- Idle video avatar (blinking Vonnegut)
- Simli widget for Talk mode
- Doodle responses with trigger system
- K.V.*bot animated signature
- Text/Talk mode toggle
- Streaming chat endpoint
- ElevenLabs TTS endpoint

**In progress:**
- Full LiveKit + Simli integration (RAG in voice mode)
- Reading context awareness in voice mode

**Next priorities:**
1. Test Simli widget with real conversations
2. Curate Tier 2 corpus (50 best passages)
3. Optimize system prompt for voice
4. Deploy LiveKit agent backend

---

## Disclaimer

Vonnebot is an AI tool trained on Kurt Vonnegut's writings to offer readers additional context and insights. It's a way to engage with his work interactively—not a literal channeling of Vonnegut himself. Born in 1922, he had his own views on technology; while we think he might have found this intriguing, we acknowledge this is just an approximation.

**This project is not affiliated with or endorsed by the Vonnegut estate.**

---

*"Listen. If this isn't nice, what is?"*
