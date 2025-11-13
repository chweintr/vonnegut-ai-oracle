# Railway Deployment Guide

## Quick Setup

### 1. Environment Variables

In your Railway project dashboard, add these environment variables:

```
OPENAI_API_KEY=sk-your-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key (optional, for voice)
ELEVENLABS_VOICE_ID=your-voice-id (optional, for voice)
```

**To add in Railway:**
1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Click "+ New Variable"
5. Add each variable above

### 2. Deploy

Railway will automatically deploy from your git branch. The `railway.json` file specifies:
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app_demo.py`

### 3. Access

Once deployed, Railway provides a URL like:
`https://your-app-name.up.railway.app`

Password to access: `tralfamadore`

## Current Deployment Status

**Active File:** `app_demo.py`
- Main reading pane (center/wide)
- AI chat sidebar (right)
- Optimized for demo/presentation

**Alternative Versions:**
- `app.py` - Original chat-only version
- `app_learning_guide.py` - Dual-tab version

To switch versions, update `railway.json`:
```json
"startCommand": "streamlit run [app.py|app_demo.py|app_learning_guide.py] ..."
```

## Checking Deployment

### View Logs
1. Railway dashboard → your service
2. Click "Deployments" tab
3. Click latest deployment
4. View build and runtime logs

### Common Issues

**Build fails:**
- Check `requirements.txt` syntax
- Verify all dependencies are compatible

**App won't start:**
- Check Railway logs for errors
- Verify environment variables are set
- Ensure PORT is not hardcoded (use `$PORT`)

**API errors:**
- Verify OPENAI_API_KEY is valid
- Check OpenAI account has credits
- Test keys locally first

## Testing Before Deploy

```bash
# Test locally with Railway env vars
export OPENAI_API_KEY=sk-your-key
export ELEVENLABS_API_KEY=your-key
export ELEVENLABS_VOICE_ID=your-id

streamlit run app_demo.py
```

Visit: `http://localhost:8501`

## Railway CLI (Optional)

Install Railway CLI for easier management:

```bash
# Install
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Set environment variable
railway variables set OPENAI_API_KEY=sk-...

# Deploy manually
railway up
```

## Security Notes

✅ **Safe:**
- Environment variables (not in code)
- `.env` is gitignored
- API keys in Railway dashboard only

❌ **Never:**
- Commit API keys to git
- Share `.env` file
- Hardcode keys in code
- Push `.env` to repository

## Cost Monitoring

**OpenAI API:**
- GPT-4: ~$0.03 per 1K tokens input, $0.06 output
- Average conversation: ~$0.10-0.30
- Monitor at: https://platform.openai.com/usage

**ElevenLabs:**
- ~$0.30 per 1K characters
- Voice responses add cost
- Consider making voice optional

**Railway:**
- Free tier: $5 credit/month
- Hobby plan: $5/month + usage
- Monitor at Railway dashboard

## Performance Tips

**Reduce costs:**
- Set usage limits in OpenAI dashboard
- Make voice optional (it's expensive)
- Cache responses where possible
- Use GPT-3.5-turbo for testing

**Improve speed:**
- Use `temperature=0.7` (faster, cheaper)
- Reduce `max_tokens` if responses too long
- Enable Railway caching

## Status Check

Current setup status:
- ✅ API keys secured (not in repo)
- ✅ `.env` gitignored
- ✅ Railway config updated for `app_demo.py`
- ⏳ Deploy to Railway (push to trigger)
- ⏳ Set environment variables in Railway
- ⏳ Test deployed URL

## Next Steps

1. **Push to git** - Railway auto-deploys
2. **Add env vars** in Railway dashboard
3. **Check deployment logs**
4. **Test the live URL**
5. **Share with IU lawyers** for demo

---

*Railway will auto-deploy when you push to your branch*
