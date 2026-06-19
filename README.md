# PDF RAG Starter (Python)

Quickstart:

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Optional: start Weaviate if you want vector search support:

```powershell
docker compose up -d
```

3. Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:
- `POST /upload` multipart form with `file` field
- `POST /ask` JSON `{ "docId": "...", "question": "..." }`

Environment: copy `.env.example` to `.env` and adjust.

Notes:
- This starter uses `sentence-transformers` locally for embeddings.
- If `WEAVIATE_URL` is configured, the vector store will attempt to upsert/query against Weaviate.
- The LLM adapter is a placeholder and returns a fallback answer unless `GEMINI_API_URL` is configured.
