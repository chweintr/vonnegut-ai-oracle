# Phase 2: Full RAG + Voice Integration Plan

## Current State
- **Working**: Simli widget with basic Vonnegut persona (no RAG, no reading context)
- **Problem**: Simli's hosted agent can't access our backend, corpus, or see what user is reading

---

## Architecture for Full Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER BROWSER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │ Reading     │  │ Simli       │  │ Microphone                      │  │
│  │ Pane        │  │ Avatar      │  │ (WebRTC audio to LiveKit)       │  │
│  │ (visible    │  │ (video)     │  │                                 │  │
│  │  passage)   │  │             │  │                                 │  │
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

### Sweet Spot Recommendations
- **System prompt**: 500-800 words max (currently ~1000)
- **RAG chunks**: Top 2 results, 200-300 words each
- **LLM max tokens**: 150-200 (conversational, not essays)
- **ElevenLabs**: Use "turbo" model for lower latency

---

## What to Ask Vonnegut Scholars

### 1. Essential Biographical Facts (for accuracy)
- "What are the most commonly misquoted or misattributed Vonnegut facts?"
- "What dates/events do people get wrong most often?"
- "Are there any persistent myths about Vonnegut we should avoid?"

### 2. Voice & Speech Patterns (for persona)
- "How would you describe his actual speaking voice vs. his writing voice?"
- "What phrases or verbal tics did he use in interviews vs. on the page?"
- "How did his speaking style change over the decades?"

### 3. Teaching Philosophy (for pedagogical moods)
- "What was his actual teaching style at Iowa? Socratic? Lecture? Workshop?"
- "How did he balance being a 'star' with being a working teacher?"
- "What feedback did students say he gave? Encouraging? Tough? Cryptic?"

### 4. Corpus Prioritization (for RAG efficiency)
**Key question**: "If we can only use 50-100 passages for grounding, which would capture the essential Vonnegut?"

Candidates to ask about:
- **Interviews**: Which are most representative? (Playboy? Paris Review? Wampeters?)
- **Essays**: A Man Without a Country vs. Palm Sunday vs. Fates Worse Than Death?
- **Letters**: Are the collected letters worth including? Which recipients?
- **Speeches**: Graduation speeches? Humanist speeches?

### 5. Thematic Clusters (for smarter retrieval)
- "What are the 5-10 themes he returned to obsessively?"
- "Which books/passages best represent each theme?"
- "Are there 'hidden gem' passages scholars love that general readers miss?"

### 6. Rights & Sensitivities
- "What would the estate care about most if they saw this?"
- "Are there topics/periods he wouldn't want AI 'channeling'?"
- "How would you frame the disclaimer to be respectful?"

---

## Corpus Strategy for Low Latency

### Tiered Approach

**Tier 1: Always Available (baked into system prompt)**
~500 words of essential "Vonnegut DNA":
- Key biographical facts
- 5-10 signature phrases with attribution
- Core philosophical positions
- Speech pattern examples

**Tier 2: Fast RAG (small, high-quality)**
~50 passages, pre-embedded:
- Most quotable moments from major works
- Key interview responses on common topics
- Biographical anecdotes he told repeatedly

**Tier 3: Deep RAG (on-demand)**
Full corpus, but only searched when:
- User asks about a specific book
- User asks a detailed/scholarly question
- System detects the question needs grounding

### Suggested Passage Selection Criteria
Ask scholars: "For each passage, rate 1-5 on:"
1. **Quotability** - Would Vonnegut have repeated this?
2. **Representativeness** - Does this sound like him?
3. **Uniqueness** - Does this add something the prompt can't?
4. **Brevity** - Is it under 200 words?

---

## Implementation Steps

### Step 1: Optimize Current Setup
- [ ] Trim system prompt to ~600 words
- [ ] Test latency with current Simli agent
- [ ] Benchmark: what's acceptable? 2 seconds? 3?

### Step 2: Set Up LiveKit Agent Service
- [ ] Deploy `vonnebot_agent.py` to Railway as separate service
- [ ] Configure LiveKit Cloud project
- [ ] Test basic voice-to-voice (no RAG yet)

### Step 3: Add RAG to Agent
- [ ] Integrate corpus search into agent pipeline
- [ ] Implement tiered retrieval (fast vs. deep)
- [ ] Test latency impact

### Step 4: Add Reading Context
- [ ] Pass visible passage from frontend to agent
- [ ] Agent includes passage in LLM context
- [ ] Test: "What do you think of this passage?" works

### Step 5: Optimize
- [ ] Profile each pipeline step
- [ ] Implement streaming where possible
- [ ] A/B test prompt lengths

---

## Questions for You

1. **Acceptable latency?** 2 seconds? 3? What's the UX breaking point?
2. **Simli agent system prompt**: How long is it currently? Can you paste it?
3. **Corpus size**: How many passages do we have? Can we curate to ~50 "best"?
4. **ElevenLabs model**: Are you using "turbo" or standard?
5. **Budget**: LiveKit and agent hosting will add costs. Rough limits?

---

## For the Scholar Meeting

### Deliverable Request
Ask if they'd be willing to:
1. **Review our 50-passage shortlist** - "Does this capture him?"
2. **Record themselves doing Vonnegut voice** - Reference for persona tuning
3. **Red-team the bot** - "Try to make it say something he wouldn't"
4. **Suggest 'test questions'** - "A real Vonnegut would answer X this way"

### What to Bring
- Demo of current (non-RAG) voice mode
- List of passages we're considering
- The system prompt for their review
- Specific questions about his speaking style

---

*"I tell you, we are here on Earth to fart around, and don't let anybody tell you different." — But how fast can we fart around? That's the latency question.*
