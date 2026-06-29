# Deployment Plan — Vercel + Railway

> **Frontend** → Vercel (static HTML/CSS/JS)  
> **Backend** → Railway (FastAPI + ChromaDB + Embedding Model)

> Reference: [architecture.md](file:///d:/NEXTLEAP%20GEN%20AI/RAG_CHATBOT/docs/architecture.md) · [implementation-plan.md](file:///d:/NEXTLEAP%20GEN%20AI/RAG_CHATBOT/docs/implementation-plan.md)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Railway — Backend Deployment](#3-railway--backend-deployment)
4. [Vercel — Frontend Deployment](#4-vercel--frontend-deployment)
5. [Connecting Frontend to Backend](#5-connecting-frontend-to-backend)
6. [Data Ingestion on Railway](#6-data-ingestion-on-railway)
7. [Environment Variables Reference](#7-environment-variables-reference)
8. [CI/CD — Auto-Deploy from GitHub](#8-cicd--auto-deploy-from-github)
9. [Monitoring & Logs](#9-monitoring--logs)
10. [Cost Breakdown](#10-cost-breakdown)
11. [Troubleshooting](#11-troubleshooting)
12. [Deployment Checklist](#12-deployment-checklist)

---

## 1. Architecture Overview

```mermaid
flowchart LR
    subgraph VERCEL["Vercel (Frontend)"]
        FE["Static Site<br>HTML / CSS / JS"]
    end

    subgraph RAILWAY["Railway (Backend)"]
        API["FastAPI Server<br>Uvicorn"]
        EMB["Embedding Model<br>BGE-small-en-v1.5"]
        VDB["ChromaDB<br>(Persistent Volume)"]
        GRD["Guardrails"]
    end

    subgraph EXTERNAL["External"]
        GROQ["Groq API<br>llama-3.3-70b"]
    end

    USER["User"] -->|HTTPS| FE
    FE -->|"POST /api/chat"| API
    API --> GRD
    GRD --> EMB
    EMB --> VDB
    API -->|LLM call| GROQ
```

| Component | Platform | What Gets Deployed |
|-----------|----------|--------------------|
| **Frontend** | Vercel | `frontend/` directory (index.html, styles.css, script.js) |
| **Backend** | Railway | Docker container with FastAPI, ChromaDB, BGE-small embedding model |
| **Vector Store** | Railway | ChromaDB on a persistent volume (`/app/data/vectorstore`) |
| **LLM** | Groq (external) | API call — nothing to deploy |

---

## 2. Prerequisites

### Accounts Required

| Service | Sign Up | Free Tier |
|---------|---------|-----------|
| **GitHub** | [github.com](https://github.com) | ✅ Free |
| **Railway** | [railway.app](https://railway.app) | $5 free trial credit, then $5/mo + usage |
| **Vercel** | [vercel.com](https://vercel.com) | ✅ Free (Hobby plan) |
| **Groq** | [console.groq.com](https://console.groq.com) | ✅ Free (rate-limited) |

### Local Tools

```bash
# Required
git --version          # 2.40+
node --version         # 18+ (for Vercel CLI)
python --version       # 3.10+

# Install CLIs
npm install -g vercel
npm install -g @railway/cli
```

### Push Code to GitHub

Your project must be in a GitHub repository. If it isn't already:

```bash
cd "d:\NEXTLEAP GEN AI\RAG_CHATBOT"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<your-username>/RAG_CHATBOT.git
git push -u origin main
```

---

## 3. Railway — Backend Deployment

### 3.1 Create the Dockerfile

Create this file at the project root:

```dockerfile
# File: Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Pre-download the embedding model (~130 MB)
# This avoids downloading on every container restart
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY .env.example ./.env.example

# Expose port (Railway auto-detects this)
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Add a `.dockerignore` at the project root:

```
# File: .dockerignore
venv/
.env
.git/
.pytest_cache/
__pycache__/
*.pyc
docs/
tests/
scratch/
frontend/
stitch_hdfc_mutual_fund_chatbot/
ui/
*.md
!requirements.txt
```

### 3.2 Deploy to Railway (GUI Method)

1. **Go to** [railway.app](https://railway.app) and sign in with GitHub

2. **Create a New Project**
   - Click **"New Project"** → **"Deploy from GitHub Repo"**
   - Select your `RAG_CHATBOT` repository
   - Railway auto-detects the `Dockerfile`

3. **Add Environment Variables**
   - Go to your service → **Variables** tab
   - Add each variable:

   | Variable | Value |
   |----------|-------|
   | `GROQ_API_KEY` | `gsk_xxxxxxxxxxxxxxxx` |
   | `LLM_PROVIDER` | `groq` |
   | `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` |
   | `CHROMA_PERSIST_DIR` | `/app/data/vectorstore/chroma_db` |
   | `CHROMA_COLLECTION_NAME` | `hdfc_mutual_funds` |
   | `RETRIEVAL_TOP_K` | `5` |
   | `RERANK_TOP_K` | `3` |
   | `LLM_TEMPERATURE` | `0.1` |
   | `LLM_MAX_TOKENS` | `256` |
   | `SCRAPE_DELAY_SECONDS` | `2` |
   | `API_HOST` | `0.0.0.0` |
   | `API_PORT` | `8000` |
   | `PORT` | `8000` |

4. **Attach a Persistent Volume** (for ChromaDB data)
   - Go to your service → **Volumes** tab
   - Click **"New Volume"**
   - Mount path: `/app/data/vectorstore`
   - Size: 1 GB (more than enough for 168 chunks)

5. **Generate a Public URL**
   - Go to **Settings** → **Networking** → **Public Networking**
   - Click **"Generate Domain"**
   - You'll get a URL like: `https://rag-chatbot-production-xxxx.up.railway.app`

6. **Verify Deployment**
   - Visit `https://your-app.up.railway.app/api/health`
   - Expected response:
   ```json
   {
     "status": "healthy",
     "vector_store_docs": 168,
     "last_ingestion": "Unknown"
   }
   ```

### 3.3 Deploy to Railway (CLI Method)

```bash
# Login to Railway
railway login

# Initialize project (link to existing GitHub repo)
railway init

# Set environment variables
railway variables set GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
railway variables set LLM_PROVIDER=groq
railway variables set EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
railway variables set CHROMA_PERSIST_DIR=/app/data/vectorstore/chroma_db
railway variables set CHROMA_COLLECTION_NAME=hdfc_mutual_funds
railway variables set RETRIEVAL_TOP_K=5
railway variables set RERANK_TOP_K=3
railway variables set LLM_TEMPERATURE=0.1
railway variables set LLM_MAX_TOKENS=256
railway variables set SCRAPE_DELAY_SECONDS=2
railway variables set API_HOST=0.0.0.0
railway variables set API_PORT=8000
railway variables set PORT=8000

# Add a persistent volume
railway volume add --mount /app/data/vectorstore

# Deploy
railway up

# Get the public URL
railway domain
```

### 3.4 Run Data Ingestion on Railway

After the first deploy, the ChromaDB volume is empty. You need to run ingestion once:

```bash
# Option 1: Railway CLI
railway run python scripts/run_ingestion.py

# Option 2: Railway shell (via Dashboard)
# Go to your service → click "Shell" tab → run:
python scripts/run_ingestion.py
```

Expected output:

```
Ingestion complete.
  Schemes processed: 12
  Attribute chunks:  132
  Section chunks:     24
  Full-doc chunks:    12
  Total chunks:      168
  ChromaDB collection size: 168
```

> [!IMPORTANT]
> **You must run ingestion at least once** after the first deployment. Without it, ChromaDB is empty and all queries will return "I don't have enough information."

---

## 4. Vercel — Frontend Deployment

### 4.1 Prepare the Frontend

Before deploying, update `frontend/script.js` to point to your Railway backend URL.

**Current code** (local-only):
```javascript
// No API URL configured — sendMessage() doesn't call the backend yet
```

**Updated code** — add the API call to `sendMessage()` in [script.js](file:///d:/NEXTLEAP%20GEN%20AI/RAG_CHATBOT/frontend/script.js):

```javascript
// At the top of script.js, set your Railway backend URL
const API_BASE_URL = "https://your-app.up.railway.app";

// ... existing code ...

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Show user message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content" style="align-items: flex-end;">
            <div class="message-bubble">${text}</div>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    userInput.value = '';
    chatArea.scrollTop = chatArea.scrollHeight;

    // Call the Railway backend
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text }),
        });
        const data = await response.json();

        // Show bot response
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot';
        botDiv.innerHTML = `
            <div class="bot-avatar"><i class="ph ph-robot"></i></div>
            <div class="message-content">
                <div class="bot-name">HDFC Assistant</div>
                <div class="message-bubble">${data.answer}</div>
            </div>
        `;
        chatContainer.appendChild(botDiv);
    } catch (error) {
        // Show error message
        const errDiv = document.createElement('div');
        errDiv.className = 'message bot';
        errDiv.innerHTML = `
            <div class="bot-avatar"><i class="ph ph-robot"></i></div>
            <div class="message-content">
                <div class="bot-name">HDFC Assistant</div>
                <div class="message-bubble">Sorry, something went wrong. Please try again.</div>
            </div>
        `;
        chatContainer.appendChild(errDiv);
    }

    chatArea.scrollTop = chatArea.scrollHeight;
}
```

> [!CAUTION]
> Replace `https://your-app.up.railway.app` with the actual Railway domain you generated in Step 3.2.5.

### 4.2 Deploy to Vercel (GUI Method)

1. **Go to** [vercel.com](https://vercel.com) and sign in with GitHub

2. **Import Project**
   - Click **"Add New"** → **"Project"**
   - Select your `RAG_CHATBOT` repository

3. **Configure Build Settings**

   | Setting | Value |
   |---------|-------|
   | **Framework Preset** | Other |
   | **Root Directory** | `frontend` |
   | **Build Command** | *(leave empty — no build needed for static files)* |
   | **Output Directory** | `.` |

4. **Deploy**
   - Click **"Deploy"**
   - Vercel will assign a URL like: `https://rag-chatbot-xxxx.vercel.app`

5. **Verify**
   - Visit your Vercel URL
   - The chat UI should load
   - Send a test question — it should hit your Railway backend and return an answer

### 4.3 Deploy to Vercel (CLI Method)

```bash
# Navigate to the frontend directory
cd "d:\NEXTLEAP GEN AI\RAG_CHATBOT\frontend"

# Login to Vercel
vercel login

# Deploy (follow the prompts)
vercel

# Prompts:
#   Set up and deploy? → Y
#   Which scope? → your account
#   Link to existing project? → N
#   Project name? → hdfc-mutual-fund-faq
#   Directory ./ is the root? → Y
#   Override settings? → N

# Deploy to production
vercel --prod
```

### 4.4 Custom Domain (Optional)

```bash
# Add a custom domain via Vercel CLI
vercel domains add yourdomain.com

# Or via Vercel Dashboard:
# Project → Settings → Domains → Add
```

---

## 5. Connecting Frontend to Backend

### 5.1 CORS Configuration

The Railway backend must allow requests from your Vercel domain. The current [server.py](file:///d:/NEXTLEAP%20GEN%20AI/RAG_CHATBOT/src/api/server.py) has `allow_origins=["*"]` which works, but for production tighten it:

```python
# src/api/server.py — update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rag-chatbot-xxxx.vercel.app",   # Your Vercel URL
        "https://yourdomain.com",                  # Custom domain (if any)
        "http://localhost:3000",                    # Local dev
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

### 5.2 Connection Flow

```mermaid
sequenceDiagram
    actor User
    participant Vercel as Vercel<br>(Frontend)
    participant Railway as Railway<br>(Backend)
    participant Groq as Groq API

    User->>Vercel: Opens chat UI
    Vercel-->>User: Serves index.html + CSS + JS
    User->>Vercel: Types a question
    Note over Vercel: JavaScript runs in browser
    Vercel->>Railway: POST /api/chat {query}
    Railway->>Railway: Classify → Embed → Search ChromaDB
    Railway->>Groq: LLM prompt + context
    Groq-->>Railway: Generated answer
    Railway->>Railway: Validate output (guardrails)
    Railway-->>Vercel: JSON response
    Vercel-->>User: Displays answer
```

### 5.3 Environment-Based API URL

To avoid hardcoding the Railway URL, use Vercel environment variables:

1. **Vercel Dashboard** → Project → **Settings** → **Environment Variables**
2. Add: `VITE_API_URL` = `https://your-app.up.railway.app`

Then in `script.js`:

```javascript
// This won't work directly in plain JS (no build step), so for a static site
// you can use a simple config approach:

// Option A: Hardcode the URL (simplest for static sites)
const API_BASE_URL = "https://your-app.up.railway.app";

// Option B: Detect environment automatically
const API_BASE_URL = window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://your-app.up.railway.app";
```

---

## 6. Data Ingestion on Railway

### 6.1 First-Time Ingestion

```bash
# Via Railway CLI (from your local machine)
railway run python scripts/run_ingestion.py
```

### 6.2 Re-Ingestion (Data Refresh)

When you want to refresh scheme data (NAV changes, etc.):

```bash
# Re-run the scraper + ingestion pipeline
railway run python scripts/run_ingestion.py
```

### 6.3 Scheduled Refresh with Railway Cron Jobs

Railway supports cron-triggered services for automated data refresh:

1. **Create a separate Railway service** in the same project
2. Set it as a **Cron Job**:
   - Schedule: `0 2 * * 0` (every Sunday at 2 AM UTC)
   - Command: `python scripts/run_ingestion.py`
3. This re-scrapes Groww and refreshes the ChromaDB data weekly

> [!NOTE]
> The persistent volume is shared across services in the same Railway project, so the cron job writes to the same ChromaDB that the API reads from.

---

## 7. Environment Variables Reference

### Railway (Backend)

| Variable | Value | Required |
|----------|-------|----------|
| `GROQ_API_KEY` | Your Groq API key | ✅ Yes |
| `LLM_PROVIDER` | `groq` | ✅ Yes |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | ✅ Yes |
| `CHROMA_PERSIST_DIR` | `/app/data/vectorstore/chroma_db` | ✅ Yes |
| `CHROMA_COLLECTION_NAME` | `hdfc_mutual_funds` | ✅ Yes |
| `RETRIEVAL_TOP_K` | `5` | Optional (default: 5) |
| `RERANK_TOP_K` | `3` | Optional (default: 3) |
| `LLM_TEMPERATURE` | `0.1` | Optional (default: 0.1) |
| `LLM_MAX_TOKENS` | `256` | Optional (default: 256) |
| `SCRAPE_DELAY_SECONDS` | `2` | Optional (default: 2) |
| `API_HOST` | `0.0.0.0` | ✅ Yes |
| `API_PORT` | `8000` | ✅ Yes |
| `PORT` | `8000` | ✅ Yes (Railway reads this) |

### Vercel (Frontend)

No environment variables needed for a static site. The API URL is set directly in `script.js`.

---

## 8. CI/CD — Auto-Deploy from GitHub

Both Vercel and Railway support **automatic deployments on git push**.

### How It Works

```mermaid
flowchart LR
    A["git push<br>to main"] --> B["GitHub"]
    B --> C["Railway<br>(rebuilds backend)"]
    B --> D["Vercel<br>(redeploys frontend)"]

    style A fill:#1a1a2e,stroke:#e94560,color:#fff
    style B fill:#1a1a2e,stroke:#0f3460,color:#fff
    style C fill:#1a1a2e,stroke:#533483,color:#fff
    style D fill:#1a1a2e,stroke:#533483,color:#fff
```

### Railway Auto-Deploy

- **Enabled by default** when you deploy from a GitHub repo
- Every push to `main` triggers a new build + deploy
- Rollback: click any previous deployment in the Railway dashboard

### Vercel Auto-Deploy

- **Enabled by default** when you import a GitHub repo
- Every push to `main` deploys to production
- PRs get automatic **preview deployments** (unique URL per PR)

### Adding Tests Before Deploy

Create `.github/workflows/test.yml` to run tests on every push:

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --tb=short
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

> [!TIP]
> Add `GROQ_API_KEY` to your GitHub repository secrets: **Settings → Secrets and Variables → Actions → New repository secret**.

---

## 9. Monitoring & Logs

### Railway

| Feature | How to Access |
|---------|---------------|
| **Live logs** | Railway Dashboard → Service → **Logs** tab |
| **Metrics** (CPU, RAM) | Railway Dashboard → Service → **Metrics** tab |
| **Health check** | `GET https://your-app.up.railway.app/api/health` |
| **Deploy history** | Railway Dashboard → Service → **Deployments** tab |

### Vercel

| Feature | How to Access |
|---------|---------------|
| **Deploy logs** | Vercel Dashboard → Project → **Deployments** |
| **Analytics** | Vercel Dashboard → Project → **Analytics** (Hobby plan: basic) |
| **Edge network status** | [vercel.com/status](https://vercel.com/status) |

### External Uptime Monitoring (Free)

Set up a free uptime monitor to alert you if the backend goes down:

| Service | Free Tier | Setup |
|---------|-----------|-------|
| [UptimeRobot](https://uptimerobot.com) | 50 monitors, 5-min checks | Monitor `https://your-app.up.railway.app/api/health` |
| [Better Stack](https://betterstack.com) | 10 monitors, 3-min checks | Same URL |

---

## 10. Cost Breakdown

### Monthly Cost Estimate

| Service | Plan | Cost | What You Get |
|---------|------|------|-------------|
| **Vercel** | Hobby (Free) | **$0** | 100 GB bandwidth, auto-SSL, CDN, preview deploys |
| **Railway** | Hobby | **$5 base** + ~$2–5 usage | 8 GB RAM, 8 vCPU, persistent volumes, auto-deploy |
| **Groq** | Free | **$0** | 30 RPM, 1K RPD, 12K TPM |
| **GitHub** | Free | **$0** | Unlimited repos, Actions (2K min/mo) |
| **UptimeRobot** | Free | **$0** | 50 monitors |
| | | | |
| **Total** | | **~$5–10/mo** | |

### Railway Usage Pricing (Beyond $5 Base)

| Resource | Cost |
|----------|------|
| vCPU | $0.000463 / minute |
| Memory | $0.000231 / GB / minute |
| Disk | $0.000231 / GB / minute |

> [!NOTE]
> For this project (small FastAPI app, ~130 MB model, 168-chunk ChromaDB), Railway usage costs are typically **$2–5/month** on top of the $5 base. Total: **~$7–10/month**.

---

## 11. Troubleshooting

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| **Frontend shows "Sorry, something went wrong"** | API URL mismatch or CORS error | Check `API_BASE_URL` in `script.js` matches your Railway domain. Check browser console for CORS errors. |
| **Railway build fails** | Missing dependencies or Dockerfile error | Check Railway build logs. Ensure `requirements.txt` is up to date. |
| **"I don't have enough information"** for all queries | ChromaDB is empty — ingestion hasn't run | Run `railway run python scripts/run_ingestion.py` |
| **Slow first response (~5–10s)** | Embedding model loading on cold start | Railway keeps containers warm on Hobby plan. If cold starts occur, the first request loads the ~130 MB model. |
| **Groq API errors** | Rate limit exceeded (30 RPM free tier) | Wait 1 minute, or upgrade Groq plan. |
| **Railway container crashes** | Out of memory | Check Railway metrics. The app needs ~500 MB–1 GB RAM. Ensure Railway service has enough memory allocated. |
| **Vercel deploy fails** | Wrong root directory | Ensure root directory is set to `frontend` in Vercel project settings. |
| **ChromaDB data lost after redeploy** | Volume not mounted | Ensure persistent volume is attached at `/app/data/vectorstore` in Railway. |

### Useful Debug Commands

```bash
# Check Railway deployment status
railway status

# View Railway logs
railway logs

# Open a shell in the Railway container
railway shell

# Test the API directly
curl https://your-app.up.railway.app/api/health

curl -X POST https://your-app.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the expense ratio of HDFC Mid Cap Fund?"}'
```

---

## 12. Deployment Checklist

### Step-by-Step Summary

```
1. Push code to GitHub              ← prerequisite
2. Deploy backend on Railway        ← Section 3
3. Add env variables on Railway     ← Section 3.2 step 3
4. Attach persistent volume         ← Section 3.2 step 4
5. Generate public Railway URL      ← Section 3.2 step 5
6. Run data ingestion               ← Section 3.4
7. Update script.js with API URL    ← Section 4.1
8. Deploy frontend on Vercel        ← Section 4.2
9. Test end-to-end                  ← below
```

### Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] `Dockerfile` and `.dockerignore` created at project root
- [ ] All tests pass locally (`pytest tests/ -v`)
- [ ] `GROQ_API_KEY` is valid and working

### Railway (Backend)

- [ ] Service deployed from GitHub repo
- [ ] All environment variables set (especially `GROQ_API_KEY`, `PORT`, `CHROMA_PERSIST_DIR`)
- [ ] Persistent volume mounted at `/app/data/vectorstore`
- [ ] Public domain generated
- [ ] `/api/health` returns `{"status": "healthy"}`
- [ ] Data ingestion completed (`vector_store_docs: 168`)

### Vercel (Frontend)

- [ ] `API_BASE_URL` in `script.js` set to Railway backend URL
- [ ] Root directory set to `frontend` in Vercel settings
- [ ] Site deployed and accessible
- [ ] Chat UI loads without console errors

### End-to-End Verification

- [ ] Factual query returns a correct answer with source citation
  - Test: *"What is the expense ratio of HDFC Mid Cap Fund?"*
- [ ] Advisory query returns polite refusal
  - Test: *"Should I invest in HDFC Mid Cap Fund?"*
- [ ] PII query is blocked
  - Test: *"My PAN is ABCDE1234F, what is NAV?"*
- [ ] Response includes "Last updated from sources" footer
- [ ] Response latency < 3 seconds
- [ ] Disclaimer banner ("Facts-only. No investment advice.") is visible

---

> **Document Version:** 2.0  
> **Last Updated:** 2026-06-30  
> **Deployment Target:** Vercel (frontend) + Railway (backend)
