# Vonnegut Learning Companion — Project Overview

## What It Does
Readers explore Vonnegut's texts in an interactive pane. Highlight a line, click “Ask Kurt” or “Themes,” and the AI answers with citations from Vonnegut’s own interviews, letters, essays, and fiction. The goal: contextual commentary straight from the “horse’s mouth,” not boilerplate study-guide summaries.

## The Problem
Conventional annotations say *what* happens. They rarely explain *why* Vonnegut wrote a sentence, how it links to Dresden, Bokononism, or his family history. Students toggle between PDFs, blogs, and lecture notes, assembling context piecemeal. The result is shallow comprehension and little feel for Vonnegut’s mind.

## How This Is Different
- **Reading pane + tutor:** Highlights trigger questions without copy/paste friction.
- **Grounded answers:** Retrieval-augmented generation feeds GPT-4o with authentic Vonnegut chunks before every reply.
- **Adaptive profile:** Users declare who they are (8th grader, creative writer, historian, etc.) and the tutor adapts tone, analogies, and depth.
- **Voice + logging:** ElevenLabs TTS, transcript export, and quick actions keep the experience multimodal and reviewable.

## Technical Setup
1. **Corpus:** Public-domain stories + fair-use excerpts stored in `data/vonnegut_corpus/`. Run `python build_corpus_index.py` to chunk texts, embed them with `text-embedding-3-large`, and save `data/corpus_index.jsonl`.
2. **Reader:** A custom Streamlit component renders the text, captures selections, and returns snippets + metadata to Python.
3. **Tutor Pipeline:**
   - Merge learner profile, highlighted passage, and question.
   - Retrieve top corpus chunks via cosine similarity (`knowledge_base.py`).
   - Inject persona + references into GPT-4o prompts.
   - Optionally synthesize the reply with ElevenLabs.
4. **Sidebar:** Profile controls, quick actions (“Explain this,” “Themes”), follow-ups, voice toggle, transcript history.
5. **Avatar Mode (planned):** Tie in the existing performance-capture avatar so Kurt can respond with facial animation, gesture, and voice for classroom demos.

## Adaptive User Profiling
**Purpose:** A high-schooler in Texas and a linguistics scholar in Mumbai need different framing. Profile settings tailor analogy pools, cultural references, tone, and depth.

### Primary Personas
- General Reader
- High School Student
- Undergraduate (discipline-specific)
- Graduate/Scholar
- Creative Writer
- Educator

### Refinements
- **Region / Dialect:** City, country, idiom awareness.
- **Discipline / Purpose:** STEM vs. humanities, coursework vs. research vs. leisure.
- **Reading Experience:** New to Vonnegut, read 2–3 novels, scholar.
- **Learning Focus:** Historical context, close reading, biographical links, craft technique.
- **Response Style:** Concise vs. expansive, text vs. audio-first.
- **Accessibility:** ESL considerations, simplified syntax, screen-reader support.

### Usage Examples
- High-school student in Texas asking about time structure → explain via football season arcs or Instagram stories.
- Linguistics scholar → discuss narrative metalepsis, Genette, free indirect discourse.
- Creative writer → focus on dialogue compression and subtext.
- General reader in India → link postwar anxiety to partition literature.

### Interface
- First session: “Who are you reading as today?” plus optional follow-ups (location, discipline, purpose, preferences).
- Stored in session (future: persistent profiles via Supabase/Redis).
- Periodic prompts: “Is this style still working?” to refine adaptively.

## Development Path
| Phase | Capability | Notes |
| --- | --- | --- |
| v1 (current) | Highlight-based RAG, per-session profile form | Persona enforces grade-level tone. |
| v1.5 | Rich profile controls (region, discipline, preferences) | Added to sidebar; appended to prompts. |
| v2 | Ambient viewport context | Auto-capture paragraph even without highlight. |
| v2.5 | Persistent profiles + analytics | Requires auth + FERPA/GDPR compliance. |
| v3 | Visual avatar integration | Performance capture + live gestures/voice. |
| v4 | Multi-author “Vonneguides” | Same pipeline for other estates/publishers. |

## Recommended Expansions
### AR Glasses Mode
Overlay annotations on physical books (Meta Ray-Ban, Apple Vision Pro, Glass Enterprise). Eye-tracking detects confusion, invites questions, shares heat maps with educators, while keeping user data opt-in and anonymized.

### Educator & Publisher Dashboards
- See which passages spark questions.
- Track misconception clusters.
- Build guided reading paths.
- Provide anonymized engagement analytics to estates/publishers.

### Multi-User Collaboration
Book clubs or classrooms can surface shared questions, vote on prompts, and receive a collective Kurt response.

### Voice & Avatar Customization
Multiple interaction modes: text-only, voice-only, or full avatar. Mood calibration (conversational vs. lecture mode) and gesture control.

### Longitudinal Learning Profiles
Track reading history, question complexity, unresolved curiosities. Use to personalize future sessions (“Last month we discussed Tralfamadorian time—want to connect that to Cat’s Cradle?”).

## Legal & Partnership Strategy
- **Current Scope:** Fair-use excerpts + public-domain material, private deployments only.
- **Ask:** Secure limited licenses (500–1000 word snippets) from the Vonnegut estate/publishers for a controlled research pilot measuring comprehension, retention, and engagement.
- **Data Governance:** Consent-driven logging, anonymized analytics with opt-out, right-to-delete, transparent manifests for every retrieval.

## Evidence Plan
- Comprehension tests (pre/post + 2–4 week retention).
- Engagement metrics (time on text vs. conventional guides).
- Question depth scoring (factual vs. interpretive vs. creative).
- Cross-demographic cohorts (high school, undergrad, general reader) with control groups using standard study aids.

## Why It Matters
Most literary chatbots hallucinate and ignore user context. Vonnegut Companion grounds every answer in real writing and adapts to who’s asking. With proper permissions and data stewardship, the same architecture can support other authors and disciplines, turning reading into an adaptive, empathic learning experience.
