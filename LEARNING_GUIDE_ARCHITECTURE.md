# Vonnegut Learning Guide - Architecture Design

## Project Vision
An interactive learning companion that merges AI conversation with active reading. Users can read Vonnegut's works alongside an AI trained on his speeches, letters, interviews, and public domain materials. The AI acts as a literary guide, explaining themes, context, and style when users highlight passages.

## Core Features

### 1. Dual-Panel Interface
```
┌─────────────────────────────────────┬──────────────────────┐
│  Reading Pane                       │  Vonnegut Assistant  │
│  - Display uploaded texts           │  - Chat interface    │
│  - Highlight selection              │  - Voice option      │
│  - Passage annotations              │  - Disclaimer banner │
│  ├─────────────────────────────┐   │  - Context display   │
│  │ Selected Text: "So it goes" │   │                      │
│  │ [Ask Vonnegut] [Annotate]   │   │  User: What does     │
│  └─────────────────────────────┘   │  "So it goes" mean?  │
│                                     │                      │
│  Main text content...               │  Kurt: *In my voice, │
│  - Scrollable                       │  that phrase...      │
│  - Searchable                       │                      │
│  - Exportable notes                 │  [Voice Response]    │
└─────────────────────────────────────┴──────────────────────┘
```

### 2. Interaction Modes

**Mode A: Free Conversation** (existing)
- Ask general questions about Vonnegut, his life, themes, writing
- No specific text reference

**Mode B: Passage Analysis** (NEW)
1. User highlights text in reading pane
2. Selection appears in assistant sidebar with context
3. User can:
   - "Explain this passage"
   - "What's the significance?"
   - "Relate to Vonnegut's life"
   - "Identify literary devices"
4. AI responds with passage context + Vonnegut knowledge

**Mode C: Document Upload & Annotation** (NEW)
- Upload .txt, .pdf files
- Select from pre-loaded public domain works
- Create personal annotations
- Export study notes

### 3. AI Enhancement Strategy

#### Current Limitation
- Only ~34KB of Vonnegut data (0.2% of target)
- Major works copyrighted until 2077

#### Expansion Plan
**Available Public Domain Sources:**
- Speeches (universities, conferences)
- Published interviews (Paris Review, Atlantic, etc.)
- Letters in academic collections
- Short stories pre-1928
- Essays and articles
- Teaching materials he published
- Documentary transcripts

**Implementation: RAG (Retrieval Augmented Generation)**
```python
# Architecture
1. Build vector database of Vonnegut materials
2. User highlights passage → retrieve relevant Vonnegut context
3. System prompt = personality + retrieved knowledge + passage
4. GPT-4 generates response as "Vonnegut"
```

**Benefits:**
- No fine-tuning required (cost-effective)
- Easy to expand knowledge base
- Maintains citation ability
- Works with current OpenAI integration

### 4. Technical Architecture

#### Frontend (Streamlit)
```python
# New components
- st.tabs() for "Chat" vs "Reading Guide" modes
- Custom HTML/JS for text selection
- st.file_uploader() for document upload
- st.session_state for passage context
- Dual columns: st.columns([2, 1])
```

#### Backend Services
```
OpenAI GPT-4
    ↓
Enhanced System Prompt
    - Vonnegut personality (existing)
    - Educational mission (new)
    - Passage context (if provided)
    - Retrieved knowledge (RAG)
    ↓
Response Generation
    ↓
ElevenLabs TTS (optional)
```

#### Data Pipeline
```
Vonnegut Materials
    ↓
Text Processing & Chunking
    ↓
Vector Embeddings (OpenAI text-embedding-ada-002)
    ↓
Vector Store (ChromaDB or FAISS)
    ↓
Retrieval on Query
```

### 5. Ethical Safeguards

#### Disclaimer System
- Prominent banner: "This is an AI simulation, not Kurt Vonnegut"
- Footer on every response: "*Simulated response based on Vonnegut's works*"
- About page explaining limitations
- No claims of actual authorship

#### Copyright Compliance
- Only public domain full texts
- Fair use excerpts for analysis (educational purpose)
- Citations for all source materials
- User-uploaded content responsibility disclaimer

#### Educational Focus
- Emphasize learning objectives
- Encourage critical thinking
- Provide historical context
- Link to original sources when possible

### 6. User Workflows

#### Workflow 1: Study a Public Domain Story
1. Open "Reading Guide" tab
2. Select "2BR02B" from library
3. Read through story in left pane
4. Highlight "Everything was perfectly swell"
5. Click "Ask Vonnegut about this"
6. AI explains irony, context, theme
7. Continue reading with new insight

#### Workflow 2: Upload Student Essay
1. Upload .txt file with Vonnegut analysis
2. Highlight thesis statement
3. Ask: "Would you agree with this interpretation?"
4. Receive thoughtful response in Vonnegut's voice
5. Export conversation as study notes

#### Workflow 3: General Discussion
1. Use "Chat" tab (existing functionality)
2. Ask about Vonnegut's life, influences
3. Receive voice response
4. Build foundational knowledge

### 7. Implementation Phases

**Phase 1: Basic Reading Interface** (Week 1)
- Dual-pane layout
- Display pre-loaded texts
- Basic text selection
- Manual copy-paste to chat

**Phase 2: Interactive Highlighting** (Week 1-2)
- JavaScript text selection handler
- Auto-populate chat with selection
- Context-aware prompting
- Passage reference in UI

**Phase 3: RAG Integration** (Week 2-3)
- Collect additional Vonnegut materials
- Build vector database
- Implement retrieval logic
- Enhanced response quality

**Phase 4: Document Management** (Week 3)
- File upload system
- Document library
- Annotation storage
- Export functionality

**Phase 5: Polish & Deploy** (Week 4)
- Enhanced disclaimers
- UI refinements
- Performance optimization
- Comprehensive testing

### 8. Technology Stack

**Current:**
- Python 3.11
- Streamlit
- OpenAI GPT-4
- ElevenLabs TTS
- Railway deployment

**New Additions:**
- ChromaDB or FAISS (vector storage)
- OpenAI Embeddings API
- PyPDF2 or pdfplumber (PDF handling)
- streamlit-javascript (text selection)
- Custom CSS/HTML for reading pane

### 9. Success Metrics

**User Engagement:**
- Time spent in reading mode
- Number of passages highlighted
- Questions asked per session
- Return user rate

**Educational Value:**
- Depth of AI responses
- Accuracy of literary analysis
- User feedback on learning
- Exported study notes

**Technical Performance:**
- Response latency (<2s)
- RAG retrieval accuracy
- UI responsiveness
- Uptime (>99%)

### 10. Future Enhancements

**Advanced Features:**
- Multi-author comparison (Vonnegut vs contemporaries)
- Timeline visualization of works
- Thematic network graphs
- Collaborative annotation
- Teacher/classroom mode
- Mobile app version

**AI Improvements:**
- Fine-tuned model on Vonnegut corpus (if legally possible)
- Multi-modal analysis (analyze book covers, illustrations)
- Writing style analyzer (compare user writing to Vonnegut's)
- Interactive writing exercises guided by "Vonnegut"

## Development Priorities

**Must Have (MVP):**
1. Dual-panel reading + chat interface ✓
2. Text selection → AI response ✓
3. Pre-loaded public domain stories ✓
4. Clear disclaimers ✓

**Should Have:**
1. RAG for enhanced knowledge ✓
2. File upload capability ✓
3. Voice response option (already exists) ✓

**Nice to Have:**
1. Annotation export
2. Multiple document formats
3. Advanced search
4. Citation tracking

## Next Steps

1. ✅ Create this architecture document
2. ⏭️ Design enhanced system prompt
3. ⏭️ Build dual-panel Streamlit UI
4. ⏭️ Implement text selection handling
5. ⏭️ Integrate RAG system
6. ⏭️ Expand knowledge base
7. ⏭️ Test with real users
8. ⏭️ Deploy updated version

---

**Document Status:** Initial Design
**Date:** 2025-11-12
**Version:** 1.0
