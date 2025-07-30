# Vonnegut AI Oracle - Version Control & Development Guide

## 🟢 STABLE VERSION (Currently Deployed)

**File:** `app.py`  
**Commit:** `ad48fec03b4311fd03d4d62a04a711ec939ce181`  
**Status:** ✅ Working in production  
**Last Updated:** July 30, 2025

### Features of Stable Version:
- **Text → Text**: Type message, get text response
- **Text → Audio**: Type message, get voice response  
- **Audio → Audio**: Click to speak, get voice response (turn-based)
- Uses `streamlit-mic-recorder` for voice input
- Manual "Send" button for text input
- Auto-submit when speech is detected in Audio mode
- Clean UI with Vonnegut video background
- Password protection

### Why This Version Works:
1. **Turn-based conversation**: User speaks → System processes → Kurt responds
2. **Clear state management**: No overlapping audio streams
3. **Simple flow**: No attempt at continuous/simultaneous conversation
4. **Proven stability**: This exact configuration has been tested and works

### Known Limitations:
- Turn-based only (not like a phone call)
- User must wait for Kurt's response before speaking again
- Slight delay between speech detection and response

---

## 🔴 EXPERIMENTAL VERSIONS (Do Not Deploy)

### Failed Attempts:
1. **Continuous voice mode**: Tried to make it like a phone call - caused infinite listening loops
2. **Auto-play with simultaneous listening**: Audio streams conflicted
3. **Various `streamlit-mic-recorder` configurations**: Most caused state management issues

### Why They Failed:
- Browser security restrictions on simultaneous audio input/output
- Streamlit's state refresh cycle conflicts with continuous audio
- `streamlit-mic-recorder` widget gets stuck when trying to listen while audio plays

---

## 📁 File Structure

```
vonnegut-ai-oracle/
├── app.py                        # ✅ STABLE - Current production version
├── vonnegut_ai_app.py           # ⚠️  Experimental version (DO NOT USE)
├── vonnegut_final.py            # 🔄 Older stable version (backup)
├── vonnegut_ai_app_fixed.py     # 🔄 Earlier version (backup)
├── railway.json                 # Railway deployment config
├── requirements.txt             # Python dependencies
└── backup-repo/                 # Git repository for deployments
    └── app.py                   # Deployed version
```

---

## 🚀 Development Strategy

### For Production (Railway):
1. **NEVER** modify `app.py` directly for experiments
2. All changes must be tested locally first
3. Use the backup-repo for deployments
4. Always test voice features before pushing

### For Experimentation:

#### Option 1: Separate Experimental App (RECOMMENDED)
```bash
# Create new Railway app
railway create vonnegut-experimental

# Use different branch
git checkout -b experimental

# Modify railway.json to use experimental.py
# Deploy to separate URL for testing
```

#### Option 2: Local Development Only
```bash
# Copy stable version for experiments
cp app.py experimental_app.py

# Run locally
streamlit run experimental_app.py

# Test thoroughly before considering for production
```

#### Option 3: Feature Branches
```bash
# Create feature branch
git checkout -b feature/continuous-voice

# Make changes
# Test locally
# Only merge if 100% working
```

---

## 🛠️ How to Deploy Updates

### For Bug Fixes to Stable Version:
```bash
cd backup-repo
# Make minimal changes to app.py
git add app.py
git commit -m "Fix: [specific issue]"
git push origin main
```

### For New Features:
1. Test in experimental environment first
2. Ensure all existing features still work
3. Document any new dependencies
4. Update this README
5. Only then update production

---

## ⚠️ Critical Rules

1. **NEVER** push untested voice features to production
2. **ALWAYS** test all three conversation modes before deploying
3. **KEEP** the turn-based structure - it's what works
4. **DOCUMENT** any changes to dependencies in requirements.txt
5. **BACKUP** before major changes

---

## 🐛 Known Issues & Solutions

### Issue: "streamlit-mic-recorder not installed"
**Solution:** Already in requirements.txt, wait 1-2 minutes for Railway to rebuild

### Issue: Voice gets stuck in listening mode
**Solution:** Revert to this stable version immediately

### Issue: Audio doesn't play
**Solution:** Check ElevenLabs API key and quotas

---

## 📝 Version History

- **v2.0** (current): Stable turn-based voice conversation
- **v1.5**: Added voice input via streamlit-mic-recorder  
- **v1.0**: Text-only version with optional voice output
- **v0.x**: Various experimental versions (deprecated)

---

## 🚨 Emergency Rollback

If production breaks:
```bash
cd backup-repo
git checkout ad48fec -- app.py
git add app.py
git commit -m "Emergency rollback to stable version"
git push origin main
```

Railway will auto-deploy the stable version within ~2 minutes.