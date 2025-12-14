# Deploying Vonnebot Agent to Railway

This guide walks you through deploying the LiveKit agent (`vonnebot_agent.py`) as a separate Railway service.

## Why a Separate Service?

The agent is a long-running process that:
- Connects to LiveKit and listens for new rooms
- Joins rooms when users click "Connect"
- Handles voice AI pipeline (STT → LLM → TTS → Simli)

Flask can't run this because it's request/response based, not persistent.

---

## Prerequisites

1. **LiveKit Cloud account** - https://cloud.livekit.io (free tier available)
2. **Simli account** - https://app.simli.com
3. **Railway account** - https://railway.app
4. **OpenAI API key** - For GPT-4o

---

## Step 1: Get LiveKit Credentials

1. Go to https://cloud.livekit.io
2. Create a new project (or use existing)
3. Go to **Settings** → **Keys**
4. Copy:
   - **API Key** (starts with `API...`)
   - **API Secret** (long string)
   - **WebSocket URL** (e.g., `wss://your-project-abc123.livekit.cloud`)

---

## Step 2: Get Simli Credentials

1. Go to https://app.simli.com
2. Navigate to your agent or create one
3. Copy:
   - **API Key** (from account settings)
   - **Face ID** (from your agent/face settings)

---

## Step 3: Create Railway Agent Service

### Option A: Using Railway Dashboard

1. Go to your Railway project (where `vonnegut-ai-oracle` is deployed)
2. Click **+ New** → **Empty Service**
3. Name it `vonnebot-agent`
4. Go to **Settings** tab:
   - **Root Directory**: Leave empty (uses repo root)
   - **Build Command**: Leave empty (uses Dockerfile)
   - **Dockerfile Path**: `Dockerfile.agent`
5. Connect to your GitHub repo (`vonnegut-ai-oracle`)

### Option B: Using Railway CLI

```bash
# Install Railway CLI if you haven't
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Create new service
railway service create vonnebot-agent

# Set the Dockerfile
railway service update --dockerfile Dockerfile.agent
```

---

## Step 4: Add Environment Variables

In Railway, go to your `vonnebot-agent` service → **Variables** tab.

Add these variables:

```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxx
SIMLI_API_KEY=your_simli_api_key
SIMLI_FACE_ID=your_face_id
OPENAI_API_KEY=sk-proj-xxxxx
HF_HOME=/tmp/huggingface
```

**Important**: The `HF_HOME` variable is required for Railway to work with the turn detector model.

---

## Step 5: Update Main Service Variables

Your main `vonnegut-ai-oracle` service also needs LiveKit variables to generate tokens:

```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxx
```

---

## Step 6: Deploy

1. Push your code to GitHub (if not already)
2. Railway will automatically build and deploy both services
3. Check logs for both services:
   - Main service should show Flask starting
   - Agent service should show "Vonnebot agent is now active"

---

## Testing

1. Open your Vonnebot site
2. Click **Talk** mode
3. Click **Start** on the Simli widget
4. Check Railway logs:
   - Main service: Should show token generation
   - Agent service: Should show "Starting Vonnebot agent session"
5. Speak and see if the avatar responds

---

## Troubleshooting

### Agent not starting

Check logs for errors. Common issues:
- Missing environment variables
- Invalid API keys
- LiveKit connection failures

### "Unrecognized model in livekit/turn-detector"

Add `HF_HOME=/tmp/huggingface` to environment variables.

### Token generation failing

Check that main service has `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET`.

### Agent not joining rooms

- Verify `LIVEKIT_URL` matches between main service and agent
- Check that LiveKit project is active
- Look at LiveKit Cloud dashboard for room activity

### Simli avatar not showing

- Verify `SIMLI_API_KEY` and `SIMLI_FACE_ID` are correct
- Check Simli dashboard for any errors

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      RAILWAY PROJECT                          │
│                                                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐  │
│  │ vonnegut-ai-oracle  │    │ vonnebot-agent              │  │
│  │ (Flask frontend)    │    │ (LiveKit agent)             │  │
│  │                     │    │                             │  │
│  │ - Serves web UI     │    │ - Listens for rooms         │  │
│  │ - Text chat API     │    │ - Voice AI pipeline         │  │
│  │ - Token generation  │    │ - Simli avatar              │  │
│  │                     │    │                             │  │
│  │ Port: 5000          │    │ No port (background)        │  │
│  └──────────┬──────────┘    └──────────────┬──────────────┘  │
│             │                              │                  │
└─────────────┼──────────────────────────────┼──────────────────┘
              │                              │
              │ generates token              │ connects
              │                              │
              ▼                              ▼
       ┌──────────────────────────────────────────┐
       │            LIVEKIT CLOUD                  │
       │         (WebRTC infrastructure)           │
       └──────────────────────────────────────────┘
```

---

## Cost Estimates

- **Railway**: ~$5-20/month depending on usage
- **LiveKit Cloud**: $0.01/min of active agent sessions
- **Simli**: Check their pricing page
- **OpenAI**: ~$0.01-0.03 per conversation turn

---

## Next Steps After Deployment

Once the agent is running, you can:

1. **Add RAG context**: Modify `vonnebot_agent.py` to include reading passage
2. **Customize voice**: Change the `voice` parameter in RealtimeModel
3. **Monitor usage**: Check LiveKit and Railway dashboards

---

*"And so it goes."* — But now it goes on Railway.
