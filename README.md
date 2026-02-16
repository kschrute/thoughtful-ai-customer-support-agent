# Thoughtful AI Customer Support Agent

A small full-stack demo:

- Python **FastAPI** backend
- **Vite + React + TypeScript** chat UI
- KB retrieval via vector similarity + fallback to **OpenAI** or **Gemini**

See live demo here [thoughtful-ai-support-agent.fly.dev](https://thoughtful-ai-support-agent.fly.dev)

## Backend (FastAPI)

### Backend setup

```bash
uv sync
```

### Configure LLM fallback

Set one of:

```bash
export OPENAI_API_KEY=...
```

or:

```bash
export GEMINI_API_KEY=...
```

Optional:

```bash
export LLM_PROVIDER=openai   # or gemini
export SIMILARITY_THRESHOLD=0.35
export CORS_ORIGIN=http://localhost:5173
```

### Backend run

```bash
uv run uvicorn backend.app:app --reload --port 8000
```

Health check: <http://localhost:8000/health>

## Frontend (Vite)

### Frontend setup

```bash
cd frontend
npm install
```

### Frontend run

```bash
npm run dev
```

Open: <http://localhost:5173>

## How it works

- The backend loads `backend/kb.json`.
- It computes a vector representation for each KB question and the user query.
- If the best cosine similarity is above `SIMILARITY_THRESHOLD`, it returns the KB answer.
- Otherwise it calls an external LLM (OpenAI or Gemini) as a fallback.

## Fly.io deployment (Docker)

- The provided `Dockerfile` builds the frontend and serves it from the FastAPI app.
- The container listens on `PORT` (default `8080`), which matches Fly.io conventions.

Typical flow:

```bash
fly launch
fly secrets set GEMINI_API_KEY=... LLM_PROVIDER=gemini
fly deploy
```
