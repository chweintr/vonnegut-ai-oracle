# Railway Environment Variable Guide

Configure these variables in your Railway project before deploying `app_learning_guide.py`.

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | ✅ | Secret key for OpenAI Chat Completions (Vonnegut tutor + chat modes). Use an org-scoped key with access to `gpt-4` or higher. |
| `ELEVENLABS_API_KEY` | Optional | Enables voice playback in Text → Audio and Audio → Audio modes. Omit (or leave blank) to disable TTS. |
| `ELEVENLABS_VOICE_ID` | Optional | ElevenLabs voice profile to synthesize Kurt's replies. Needed only if `ELEVENLABS_API_KEY` is set. |
| `STREAMLIT_SERVER_PORT` | 🚫 | Do **not** set. Railway injects the `$PORT` value automatically and the start command already consumes it. |

## Setup Steps

1. In Railway, open your project → **Variables**.
2. Add `OPENAI_API_KEY` with the same value you use locally (keep it scoped to the Learning Guide service).
3. (Optional) Add `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` if you plan to demo audio output.
4. Redeploy or restart the service so the new env vars reach `app_learning_guide.py`.

## Private Excerpt Reminder

For legal reviews, paste 500–1000 word excerpts for *Slaughterhouse-Five*, *Cat's Cradle*, and *Breakfast of Champions* into the matching files under `data/excerpts/` **before** deploying. The repo only ships placeholder files (to stay within copyright rules), so the Railway build must include your locally supplied text.

After the excerpts are in place, rebuild the semantic index locally and commit the generated `data/corpus_index.jsonl` to the deployment artifact (or run `python build_corpus_index.py` during CI) so the production app can reference the authentic materials.
