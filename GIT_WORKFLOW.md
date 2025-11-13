# Git Workflow Guide

## Repo Structure
```
data/
├── raw/                     # Public-domain texts (safe to commit)
├── excerpts/                # IU-only fair-use snippets (keep private unless licensed)
├── vonnegut_corpus/
│   ├── public_domain/       # OK to push
│   └── educational_fair_use/# .gitignored
└── corpus_index.jsonl       # .gitignored (rebuild locally)
```

## Recommended Process
1. **Stay on the main feature branch** (or create a short-lived branch).
2. **Keep sensitive files local:** anything under `educational_fair_use/` or `data/excerpts/` should never be added to git. `.gitignore` already blocks them.
3. **Rebuild the index locally** after adding new texts:
   ```bash
   export OPENAI_API_KEY=...
   python build_corpus_index.py
   ```
   The generated JSONL + manifest stay local; just note the build date in your commit message or README.
4. **Commit flow:**
   ```bash
   git status
   git add <safe files>
   git commit -m "Describe change"
   git push origin <branch>
   ```
5. **Private repo reminder:** Even though fair-use files are ignored, keep this repository private/password-protected when pushing to GitHub or Railway.

## Optional Two-Repo Setup
- **Public repo:** Contains code + `public_domain/`. No sensitive text.
- **Private repo:** Mirrors the project but includes `educational_fair_use/` and deployment configs. Use this when collaborating under NDA or with institutional partners.

## Need Help?
Run `git status` before every commit. If you accidentally stage a sensitive file, use `git reset <file>` or `git restore --staged <file>` before committing.
