# Adding Text Excerpts for Demo

## For IU Lawyers Demo - Fair Use Guidelines

You want to add substantial excerpts from major Vonnegut works to demonstrate the "uncanny" functionality. Here's how to do it while staying within educational fair use.

## Fair Use Framework (Educational Purpose)

✅ **Safe for Demo:**
- 500-1500 word excerpts from each major work
- Famous passages that showcase themes
- 3-5 excerpts per novel (representing ~2-5% of total)
- Clear attribution and copyright notices
- Educational/research purpose documented

✅ **Legal Backing:**
- 17 U.S.C. § 107 (Fair Use)
- Educational purpose
- Limited portion of work
- Non-commercial research/demo
- Transformative use (AI annotations)
- No market harm (demo for partnership)

## Recommended Excerpts to Add

### Slaughterhouse-Five (1969)

**Excerpt 1: Opening** (~500 words)
- "All this happened, more or less..."
- Establishes narrative voice
- Meta-fictional elements

**Excerpt 2: "So it goes"** (~300 words)
- First appearance of the phrase
- Death theme introduction

**Excerpt 3: Dresden bombing** (~800 words)
- Core traumatic scene
- Historical significance

**Excerpt 4: Tralfamadorian philosophy** (~400 words)
- Time as simultaneous
- Free will discussion

### Cat's Cradle (1963)

**Excerpt 1: Opening ("Call me Jonah")** (~400 words)
- Melville reference
- Narrator introduction

**Excerpt 2: Ice-Nine explanation** (~500 words)
- Central plot device
- Scientific metaphor

**Excerpt 3: Bokononism** (~600 words)
- Foma and granfalloons
- Religion satire

### Breakfast of Champions (1973)

**Excerpt 1: "Listen" opening** (~500 words)
- Direct address style
- Authorial presence

**Excerpt 2: Dwayne Hoover** (~400 words)
- Character introduction
- Mental breakdown themes

**Excerpt 3: Kilgore Trout** (~450 words)
- Writer character
- Meta-fiction

### Mother Night (1961)

**Excerpt 1: "We are what we pretend to be"** (~350 words)
- Famous opening moral
- Core theme

### Player Piano (1952)

**Excerpt 1: Automation dystopia** (~600 words)
- Technology critique
- Social commentary

## How to Add Excerpts

### Step 1: Create Excerpt Files

```bash
cd data/raw/

# Create files for each excerpt
touch slaughterhouse_five_excerpts.txt
touch cat_cradle_excerpts.txt
touch breakfast_of_champions_excerpts.txt
```

### Step 2: Format Each File

```
================================================================================
SLAUGHTERHOUSE-FIVE by Kurt Vonnegut
Excerpts for Educational Research - Fair Use (17 U.S.C. § 107)
================================================================================

Copyright © 1969 by Kurt Vonnegut
Published by Delacorte Press/Dell Publishing
All rights reserved

These excerpts are used for educational research purposes in demonstrating
AI-assisted literary analysis tools. This constitutes fair use under U.S.
copyright law for nonprofit educational and research purposes.

================================================================================

EXCERPT 1: Opening (Chapter 1)
Location: Pages 1-3
~500 words

All this happened, more or less. The war parts, anyway, are pretty much true.
One guy I knew really was shot in Dresden for taking a teapot that wasn't his...

[Continue with excerpt text...]

================================================================================

EXCERPT 2: So It Goes (Chapter 2)
Location: Pages 23-25
~300 words

[Excerpt text...]

================================================================================

[Continue for each excerpt...]
```

### Step 3: Add Copyright Notice File

Create `data/raw/COPYRIGHT_NOTICE.txt`:

```
================================================================================
COPYRIGHT NOTICE - FAIR USE DECLARATION
================================================================================

EDUCATIONAL RESEARCH PROJECT
Vonnegut AI Literary Companion - IU Partnership Demo

PURPOSE:
This project demonstrates an AI-powered literary analysis tool for educational
use. Excerpts from copyrighted works are included under Fair Use (17 U.S.C. § 107)
for the following purposes:

1. Educational research and teaching
2. Literary criticism and analysis
3. Technology demonstration for institutional partnership
4. Nonprofit scholarly research

FAIR USE JUSTIFICATION:

Purpose & Character:
- Nonprofit educational research
- Transformative use (AI-assisted literary analysis)
- Critical commentary and teaching
- No commercial exploitation

Nature of Work:
- Published creative works of recognized literary merit
- Educational/cultural value

Amount Used:
- Limited excerpts (500-1500 words per work)
- Represents 2-5% of each source work
- Only portions necessary for educational demonstration

Market Effect:
- No substitute for original works
- Likely to increase interest in full works
- No financial harm to rights holders
- Potential partnership benefits estate

RIGHTS ACKNOWLEDGMENT:

All excerpted works remain © their respective copyright holders:
- Slaughterhouse-Five © 1969 Kurt Vonnegut
- Cat's Cradle © 1963 Kurt Vonnegut
- Breakfast of Champions © 1973 Kurt Vonnegut
- [etc.]

Rights administered by:
- The Vonnegut Trust
- Random House/Penguin Random House

PARTNERSHIP INTENT:

This demo is created specifically to demonstrate functionality for Indiana
University legal review, with the intent to:
1. Secure proper licensing agreements
2. Establish institutional partnership
3. Obtain formal permissions from Vonnegut estate
4. Develop fair compensation structure

Contact: [Your IU email]
Date: November 2025

================================================================================
```

### Step 4: Update app_demo.py to Show Excerpts

The current `app_demo.py` already auto-loads files from `data/raw/` that contain "excerpt" in the filename.

Just add your excerpt files and they'll appear in the dropdown!

## Quick Start for Demo

**Minimal viable excerpts (30 minutes of work):**

1. **Slaughterhouse-Five** - Opening + one "So it goes" scene
2. **Cat's Cradle** - Ice-Nine explanation
3. **One famous quote passage** from Breakfast of Champions

This gives enough material to show:
- AI understanding passage context
- Thematic analysis
- Biographical connections (Dresden → Slaughterhouse)
- Writing craft explanations

## Testing the Demo

After adding excerpts:

```bash
streamlit run app_demo.py
```

Test workflow:
1. Select "Slaughterhouse Five Excerpts"
2. Copy the opening paragraph
3. Paste in sidebar
4. Click "Explain"
5. AI should explain meta-fiction, narrative voice, Dresden context

If response feels generic:
- Add more context in the excerpt file
- Include chapter/page numbers
- Add brief intro notes about the passage's significance

## Legal Protection Checklist

✅ Educational purpose documented
✅ Copyright notices included
✅ Limited excerpts only (~2-5% per work)
✅ No full texts
✅ Transformative use (AI analysis)
✅ Non-commercial demo
✅ Intent to license properly documented
✅ Partnership proposal context clear

## Where to Find Clean Text

**Option 1: Manual typing**
- Most accurate
- Tedious but safe
- Proofread carefully

**Option 2: University library digital access**
- IU may have institutional access
- Can copy excerpts for research
- Document source

**Option 3: Preview on Google Books**
- Limited pages visible
- Screenshot → OCR → clean up
- Mark source clearly

❌ **Avoid:**
- Pirated PDFs
- Full text downloads
- Unattributed copying

## After IU Lawyers Approve

Once partnership moves forward:

1. **License properly:**
   - Contact Vonnegut Trust
   - Negotiate institutional license
   - Pay appropriate fees

2. **Expand legally:**
   - Add full texts if licensed
   - Include all 14 novels
   - Add short story collections

3. **Credit properly:**
   - "Licensed by The Vonnegut Trust"
   - "In partnership with IU [Department]"
   - Proper attribution on every page

## File You Need to Create

```
data/raw/
├── slaughterhouse_five_excerpts.txt  ← CREATE THIS
├── cat_cradle_excerpts.txt           ← CREATE THIS
├── breakfast_of_champions_excerpts.txt ← CREATE THIS
└── COPYRIGHT_NOTICE.txt              ← CREATE THIS
```

Then test locally before pushing to Railway.

---

**Remember:** This is a demo for partnership discussion. Once IU commits, get proper licenses!
