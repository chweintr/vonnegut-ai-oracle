# Vonnebot — Project Specification

## Project Summary

Vonnebot is an AI reading companion for Kurt Vonnegut's literature. It sees what you're reading and responds with Vonnegut's voice, wit, and unpredictable teaching style—sometimes questioning, sometimes riffing, sometimes wandering off into a story about Dresden.

The system pairs a reading interface with retrieval-augmented generation. Every answer can pull from a corpus of Vonnegut's actual words. The bot automatically knows what passage you're looking at, so there's no friction of highlighting or copy-pasting.

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

### 2. Automatic Context Awareness

The bot sees what you're reading without requiring manual selection. Current implementation sends visible text as context with every query. Future: scroll position tracking, viewport detection, or eye tracking (AR).

**Why:** Removes friction. Makes the AI feel like it's reading alongside you.

### 3. Grounded in Source Material

Responses can pull from a corpus of Vonnegut's interviews, letters, essays, and novels via RAG (retrieval-augmented generation). The bot doesn't just generate plausible Vonnegut—it cites what he actually said.

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
- Future: PDF rendering, epub support
- Auto-context: bot knows what's in viewport

### Avatar (Top Right)
- Simli-powered talking head via LiveKit
- **Design decision needed:** Realistic Vonnegut vs. abstract/stylized
  - Uncanny valley risk with realistic version
  - Estate/rights concerns
  - Vonnegut drew simple line drawings—maybe match that aesthetic?
- Future: Avatar that appears to read with you (eyes moving, nods, reactions)

### Chat (Bottom Right)
- Scrollable conversation thread
- Alternative: **Marginalia view** (annotations alongside text, like a used book)
- Input field + send button

---

## Feature Ideas (Brainstorm)

### Implemented
- [x] Automatic passage awareness (sends visible text as context)
- [x] Four conversational moods (Questioner, Riff, Storyteller, Fellow Reader)
- [x] Vonnegut persona with biographical accuracy
- [x] Public domain text library
- [x] Upload your own text
- [x] Disclaimer and proper framing

### Near-term
- [ ] **Marginalia view**: Chat appears as marginal notes alongside text
- [ ] **"So it goes" moments**: When text mentions death, bot acknowledges it in Vonnegut's understated way
- [ ] **Scroll position tracking**: More precise "what are you reading" detection
- [ ] **Annotation layer**: Highlight, bookmark, save exchanges about specific passages

### Medium-term
- [ ] **Kilgore Trout mode**: Bot speaks as Vonnegut's recurring character—weirder, more speculative
- [ ] **Drawing mode**: Occasional simple line drawings instead of text (very on-brand)
- [ ] **Text-specific personality**: Shift tone based on which book (Slaughterhouse = fragmented, Breakfast = manic, Cat's Cradle = cold)
- [ ] **Time unstuck**: For Slaughterhouse-Five, bot occasionally jumps to different passages unprompted

### Long-term
- [ ] **Writing teacher mode**: Users write their own interpretations, bot engages as Iowa Workshop instructor
- [ ] **PDF support**: Read alongside any PDF
- [ ] **AR glasses version**: Overlay annotations on physical books
- [ ] **Multi-user collaboration**: Book clubs see shared annotations

---

## Avatar Design Considerations

### The Question
Should the avatar look like Vonnegut, or something more abstract?

### Arguments for Abstract/Stylized
- Avoids uncanny valley
- Sidesteps estate/likeness rights issues
- Matches Vonnegut's own aesthetic (he drew simple line drawings)
- A silhouette, a sketch, or something symbolic might feel more appropriate

### Arguments for Realistic
- Stronger emotional connection
- "Talking to Kurt" fantasy

### Possible Approaches
1. **Simple line drawing style** (like his book illustrations)
2. **Silhouette with expressive gestures**
3. **Abstract representation** (waveform, shapes that react)
4. **Realistic but clearly labeled as simulation**

### Avatar Behavior
Current: Animate when speaking
Future:
- Appears to read with you (eyes moving across text)
- Occasional nods or reactions to passages
- Reacts differently to death mentions, humor, etc.

---

## Technical Architecture

### Current Stack
- **Frontend**: Streamlit (`vonnebot_clean.py`)
- **LLM**: OpenAI GPT-4o
- **Persona**: `prompts_base_prompt.txt` (biographical accuracy + moods)
- **Corpus**: `data/vonnegut_corpus/` (public domain + fair use excerpts)
- **RAG**: `knowledge_base.py` + `data/corpus_index.jsonl`
- **Avatar**: Simli + LiveKit (in progress)
- **Voice**: ElevenLabs TTS (optional)

### Key Files
| File | Purpose |
|------|---------|
| `vonnebot_clean.py` | Main app (clean, minimal) |
| `prompts_base_prompt.txt` | Vonnegut persona + conversational moods |
| `vonnebot_agent.py` | LiveKit agent for voice avatar |
| `knowledge_base.py` | RAG retrieval |
| `build_corpus_index.py` | Corpus embedding pipeline |

### Deployment
- **Frontend**: Railway (Streamlit)
- **Agent Backend**: Railway (separate service, LiveKit worker)
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

### Implementation Path
1. v1 (current): Per-session, no profiling
2. v1.5: User declares profile at start
3. v2: System refines based on interaction patterns
4. v3: Persistent profiles across sessions

---

## Content & Licensing

### Current Scope
- Public domain works (2BR02B, Harrison Bergeron, etc.)
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

1. **Avatar appearance**: Realistic vs. stylized?
2. **Scroll tracking precision**: How accurately do we need to know what they're reading?
3. **Text-specific personalities**: How much should the bot shift between books?
4. **Kilgore Trout mode**: Fun idea—how prominent should it be?
5. **Writing teacher feature**: Scope and complexity?
6. **Estate engagement**: When and how to approach?

---

## Current Status

**Functional prototype deployed.** Core features working:
- Reading pane with text selection
- Chat with Vonnegut persona
- Automatic context awareness
- Four conversational moods
- Public domain text library

**In progress:**
- LiveKit + Simli avatar integration
- Voice mode

**Next priorities:**
1. Get avatar working end-to-end
2. Marginalia view option
3. "So it goes" moments
4. Scroll position tracking

---

## Disclaimer

Vonnebot is an AI tool trained on Kurt Vonnegut's writings to offer readers additional context and insights. It's a way to engage with his work interactively—not a literal channeling of Vonnegut himself. Born in 1922, he had his own views on technology; while we think he might have found this intriguing, we acknowledge this is just an approximation.

**This project is not affiliated with or endorsed by the Vonnegut estate.**

---

*"Listen. If this isn't nice, what is?"*
