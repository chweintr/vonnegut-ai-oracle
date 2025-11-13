# Vonnegut Interactive Learning Guide — Stakeholder Brief

## Purpose
Deliver an educational simulation where learners "consult" Kurt Vonnegut through a grounded AI tutor. The goal is to pair primary-source reading with contextual commentary so students internalize themes, history, and craft choices more vividly than with static study guides.

## Current State
- **Application:** Streamlit front end with highlight-to-question workflow and sidebar tutor. Powered by OpenAI GPT-4o (planned upgrade) with ElevenLabs audio option.
- **Knowledge Base:** Locally built embedding index (`python build_corpus_index.py`) spanning public-domain stories, speeches, interviews, and IU-supplied excerpts. Retrieval snippets feed each response so the AI quotes real texts.
- **Compliance:** Repo ships only public-domain works and empty placeholders. Private excerpts live locally (never pushed) and are stripped of comment headers before indexing. Railway deployment instructions emphasize this separation.

## Why Additional Licensed Materials Matter
To evaluate whether authentic conversational study improves comprehension, we need limited excerpts from the best-known novels (*Slaughterhouse-Five*, *Cat's Cradle*, *Breakfast of Champions*, etc.). Without them, Vonnegut can't address the exact prose students are assigned, undercutting the educational experiment.

We seek permission for:
1. **Short, clearly labeled excerpts (500–1000 words each)** for instructional use inside a passworded demo.
2. **Embedding those excerpts** in a secure semantic index so the tutor cites the original language when answering.
3. **A time-boxed pilot** with IU faculty, librarians, and legal observers to measure learning outcomes (engagement, recall, empathy).

The system never redistributes full texts, and every excerpt remains in plain text on IU-controlled infrastructure. All responses mark themselves as "Educational simulation." No commercial usage is planned without separate agreements.

## Educational Research Goals
1. **Qualitative:** Observe whether highlight-to-conversation flow deepens literary interpretation compared to static annotations.
2. **Quantitative:** Track recall/analysis scores before vs. after using the tool.
3. **Accessibility:** Determine whether audio narration plus adaptive explanations help neurodiverse learners or English-language learners engage with Vonnegut.

## Data Governance & Next Steps
- **Local-only ingestion:** Faculty add excerpts under `data/excerpts/` on IU-managed machines, rebuild the index, and deploy from there. GitHub remains free of copyrighted text.
- **Auditability:** `data/corpus_manifest.json` lists every source path and chunk count. Stakeholders can inspect retrieval logs to confirm citations.
- **Expansion path:** If estates/publishers approve, we can add additional works (e.g., *God Bless You, Mr. Rosewater*) with watermarked snippet metadata for auditing.

## Request to Rights Holders
We request a limited, revocable license to use short excerpts from Kurt Vonnegut's major novels strictly for this closed educational pilot. The pilot's findings (impact on student comprehension and engagement) will be shared with the estate/publisher, and no broader release will occur without renewed permission.

---
**Contact:** [Name/Email Placeholder]
