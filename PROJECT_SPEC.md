# Vonnebot — Project Specification

## Project Summary

Vonnebot is an AI reading companion for Kurt Vonnegut's literature. It sees what you're reading and responds with Vonnegut's voice, wit, and unpredictable teaching style—sometimes questioning, sometimes riffing, sometimes wandering off into a story about Dresden.

The system pairs a reading interface with retrieval-augmented generation. Every answer can pull from a corpus of Vonnegut's actual words. The bot automatically knows what passage you're looking at, so there's no friction of highlighting or copy-pasting.

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

## Two Modes: Chat vs. Voice

The system behaves differently depending on interaction mode, primarily for **latency reasons**:

### Chat Mode (Text)
- **Deeper RAG access**: Can search full corpus, return longer excerpts
- **Richer responses**: Can include drawings, formatted text, longer quotes
- **Drawing mode**: Occasionally returns simple line drawings instead of text (very on-brand—Vonnegut doodled constantly)
- **No latency pressure**: User is reading, not waiting for speech

### Voice Mode (Avatar)
- **Lighter RAG**: Top 1-2 passages only, shorter excerpts
- **Concise responses**: 1-3 sentences, conversational
- **Faster pipeline**: Prioritize responsiveness over depth
- **System prompt optimization**: Keep Simli's prompt lean (~500-800 words)

**Why:** Voice conversations feel broken at 3+ seconds latency. Chat can take 5-10 seconds and feel fine because users are reading anyway.

---

## Interface Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         VONNEBOT                                 │
│           A Kurt Vonnegut Inspired Reading Companion            │
├────────────────────────────────┬────────────────────────────────┤
│                                │     ┌──────────────┐           │
│     📖 READING PANE            │     │   🎭 Avatar  │           │
│     (scrollable)               │     │   (Simli)    │           │
│                                │     └──────────────┘           │
│     - Library texts            │                                │
│     - Upload your own          │     💬 CHAT                    │
│     - PDF support (future)     │     (scrollable)               │
│                                │                                │
│     Bot sees this              │     - Conversation thread      │
│     automatically              │     - Or marginalia view       │
│                                │                                │
└────────────────────────────────┴────────────────────────────────┘
```

### Reading Pane (Left)
- Scrollable text display
- Select from library (public domain Vonnegut) or upload your own
- Current passage highlighted with gold border
- Future: PDF rendering, epub support
- Auto-context: bot knows what's in viewport

### Avatar (Top Right)
- Idle: Looping video of Vonnegut-style illustration (blinking, subtle movement)
- Active: Simli-powered talking avatar via LiveKit
- Design: Line drawing style matching Vonnegut's own illustrations
- Future: Avatar appears to read with you (eyes moving, nods, reactions)

### Chat (Bottom Right)
- Scrollable conversation thread
- Bot messages signed "— K.V." with slight rotation (handwritten feel)
- Alternative: **Marginalia view** (annotations alongside text, like a used book)
- Input field + send button

---

## Feature Ideas

### Implemented ✓
- [x] Automatic passage awareness (sends visible text as context)
- [x] Four conversational moods (Questioner, Riff, Storyteller, Fellow Reader)
- [x] Vonnegut persona with biographical accuracy
- [x] Public domain text library
- [x] Upload your own text
- [x] Disclaimer and proper framing
- [x] Typewriter-style typography (Special Elite, Libre Baskerville, Caveat)
- [x] Idle video loop avatar
- [x] Simli widget integration (basic voice mode)

### Near-term
- [ ] **Marginalia view**: Chat appears as marginal notes alongside text
- [ ] **"So it goes" moments**: When text mentions death, bot acknowledges it in Vonnegut's understated way
- [ ] **Scroll position tracking**: More precise "what are you reading" detection
- [ ] **Annotation layer**: Highlight, bookmark, save exchanges about specific passages
- [ ] **Drawing mode**: Bot occasionally returns simple asterisk doodles or line drawings

### Medium-term
- [ ] **Kilgore Trout mode**: Bot speaks as Vonnegut's recurring character—weirder, more speculative, sci-fi tangents
- [ ] **Text-specific personality**: Shift tone based on which book:
  - Slaughterhouse-Five = fragmented, time-jumping
  - Breakfast of Champions = manic, meta, fourth-wall breaking
  - Cat's Cradle = cold, ironic, Bokononist
  - God Bless You, Mr. Rosewater = warmer, more hopeful
- [ ] **Time unstuck**: For Slaughterhouse-Five, bot occasionally jumps to different passages unprompted ("Billy Pilgrim has come unstuck in time, and so have I")
- [ ] **Full LiveKit integration**: Backend RAG + reading context in voice mode

### Long-term
- [ ] **Writing teacher mode**: Users write their own interpretations, bot engages as Iowa Workshop instructor
- [ ] **PDF support**: Read alongside any PDF
- [ ] **AR glasses version**: Overlay annotations on physical books
- [ ] **Multi-user collaboration**: Book clubs see shared annotations
- [ ] **Adaptive profiling**: Bot adjusts vocabulary/depth based on user level

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
| Tiered RAG (see below) | Variable | Complexity |

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

## Avatar Design Considerations

### The Question
Should the avatar look like Vonnegut, or something more abstract?

### Current Approach
Line drawing style matching Vonnegut's own illustrations:
- Simple, slightly awkward, recognizable mustache and curly hair
- Avoids uncanny valley
- Sidesteps estate/likeness concerns
- Feels authentic to his aesthetic

### Avatar Behavior
**Current:**
- Idle loop video (blinking, subtle movement)
- Simli widget activates on voice mode

**Future:**
- Appears to read with you (eyes moving across text)
- Occasional nods or reactions to passages
- Reacts to death mentions ("So it goes" moment)
- Different expressions for different moods

---

## Technical Architecture

### Current Stack
- **Frontend**: Flask + Jinja2 templates (beautiful typewriter styling)
- **LLM**: OpenAI GPT-4o
- **Persona**: `prompts_base_prompt.txt` (biographical accuracy + moods)
- **Corpus**: `data/vonnegut_corpus/` (public domain + fair use excerpts)
- **RAG**: `knowledge_base.py` + `data/corpus_index.jsonl`
- **Avatar**: Simli widget (current), LiveKit + Simli (planned)
- **Voice**: ElevenLabs TTS

### Key Files
| File | Purpose |
|------|---------|
| `app.py` | Flask backend |
| `templates/index.html` | Main UI (typewriter styling) |
| `prompts_base_prompt.txt` | Vonnegut persona + moods |
| `vonnebot_agent.py` | LiveKit agent for full voice integration |
| `knowledge_base.py` | RAG retrieval |
| `static/vonnegut_blinking.mp4` | Idle avatar video |

### Deployment
- **Frontend**: Railway (lovely-nurturing-production)
- **Agent Backend**: Railway (vonnegut-ai-oracle) — for full LiveKit integration
- **LiveKit**: LiveKit Cloud (WebRTC infrastructure)
- **Simli**: Avatar rendering

---

## Adaptive User Profiling (Future)

Different readers need different approaches:

### Profile Categories
- General Reader — casual interest
- High School Student — age-appropriate language
- Undergraduate — discipline-specific framing
- Graduate/Scholar — technical vocabulary
- Creative Writer — craft-focused analysis
- Educator — pedagogical framing

### How It Adapts
- **Analogy selection**: High schooler gets Friday Night Lights references, scholar gets Genette's Narrative Discourse
- **Depth calibration**: Writer gets compression/subtext discussion, student gets "how characters reveal themselves"
- **Tone**: Graduate gets dry precision, general reader gets conversational warmth
- **Nudging intensity**: Beginner gets more hints, expert gets more pushback

### Implementation Path
1. v1 (current): Per-session, no profiling
2. v1.5: User declares profile at start
3. v2: System refines based on interaction patterns
4. v3: Persistent profiles across sessions

---

## Content & Licensing

### Current Scope
- Public domain works (2BR02B, Harrison Bergeron, The Big Trip Up Yonder)
- Fair-use excerpts for educational/research use
- Private deployment only

### Future Licensing Goals
- License limited snippets from Vonnegut estate/publishers
- Controlled research pilot with audit logs
- Revenue share or flat fee model at scale

---

## Evidence Strategy (For Grants/Partnerships)

### Metrics to Track
- Comprehension gains (pre/post tests)
- Engagement duration vs. traditional study aids
- Question depth (factual vs. interpretive)
- Retention (follow-up assessment)
- Qualitative feedback
- Nudge effectiveness (did users engage more deeply?)

### Study Design
- Control group: standard study guides
- Treatment group: Vonnebot
- Cross-demographic cohorts
- Target: 200-300 users for statistical validity

---

## Budget Summary

| Scenario | Labor | API | Licensing | Infra | Total |
|----------|-------|-----|-----------|-------|-------|
| Pilot (6mo, 200 users) | $15,375 | $150 | $2,500 | $300 | $18,325 |
| Scaled Year 1 (10k users) | $30,000 | $11,250 | $10,000 | $6,000 | $57,250 |
| Steady State (Year 2+) | — | $11,250 | $10,000 | $6,000 | $27,250 |

Per-user cost at scale: ~$5.73 (Year 1), ~$2.73 (steady state)

---

## Open Questions

1. **Simli system prompt limits**: How much can we stuff before latency degrades?
2. **Kilgore Trout mode**: How prominent? Toggle or emergent?
3. **Drawing mode**: How often? What triggers it?
4. **Estate engagement**: When and how to approach?
5. **LiveKit complexity**: Worth it for RAG in voice, or accept limitations?
6. **ElevenLabs model**: Turbo vs. standard? Latency vs. quality?

---

## Current Status

**Functional prototype deployed at:** `lovely-nurturing-production.up.railway.app`

**Working:**
- Beautiful typewriter-style UI
- Reading pane with auto-context
- Text chat with Vonnegut persona
- Four conversational moods
- Idle video avatar (blinking Vonnegut)
- Simli widget for basic voice mode

**In progress:**
- Full LiveKit + Simli integration (RAG in voice mode)
- Reading context awareness in voice mode

**Next priorities:**
1. Test Simli widget latency
2. Curate Tier 2 corpus (50 best passages)
3. Optimize system prompt for voice
4. Deploy LiveKit agent backend

---

## Disclaimer

Vonnebot is an AI tool trained on Kurt Vonnegut's writings to offer readers additional context and insights. It's a way to engage with his work interactively—not a literal channeling of Vonnegut himself. Born in 1922, he had his own views on technology; while we think he might have found this intriguing, we acknowledge this is just an approximation.

**This project is not affiliated with or endorsed by the Vonnegut estate.**

---

*"Listen. If this isn't nice, what is?"*
