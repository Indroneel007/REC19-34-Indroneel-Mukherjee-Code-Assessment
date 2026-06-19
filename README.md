# PDF RAG Starter (Python)

A minimal FastAPI-based PDF retrieval-augmented generation (RAG) starter.

This project lets you:
- upload a PDF document
- extract and chunk its text
- embed chunks for vector similarity
- store vectors in Weaviate or fallback local storage
- ask questions about the PDF using a simple LLM adapter

## Application overview

The main components are:
- `app/routes/upload.py` — accepts PDF uploads and kicks off processing
- `app/libs/pdf_processor.py` — extracts text, chunks documents, and creates embeddings
- `app/libs/embeddings_adapter.py` — converts text chunks into vectors
- `app/libs/weaviate_client.py` — upserts/query vectors to Weaviate, with JSON fallback
- `app/libs/retriever.py` — retrieves top-k relevant chunks for a question
- `app/libs/llm_adapter.py` — calls Gemini/Vertex or returns a fallback answer when not configured
- `app/routes/qa.py` — accepts question requests and returns answers
- `app/routes/health.py` — reports vector store and LLM health

## 1. Setup

### 1.1 Create and activate a virtual environment

#### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 1.2 Configure environment variables

Copy the example file and edit the values:

```bash
copy .env.example .env
```

Then set the values in `.env`:

```text
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=<your-weaviate-api-key>
EMBEDDING_MODEL=all-MiniLM-L6-v2

GEMINI_API_URL=
GEMINI_API_KEY=
GEMINI_PROJECT=
GEMINI_LOCATION=us-central1
GEMINI_MODEL=text-bison-001

PORT=8000
```

### 1.3 Optional: start Weaviate

If you want full vector search support and have Docker installed:

```powershell
docker compose up -d
```

Verify Weaviate is available:

```bash
curl http://localhost:8080/v1/.well-known/ready
```

If Docker is not available, the project will still run using local fallback storage.

## 2. Run the server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at `http://127.0.0.1:8000`.

## 3. API endpoints

### Upload a PDF

`POST /upload`

- multipart form field: `file`

Example:
```bash
curl.exe -F "file=@C:\path\to\document.pdf" http://127.0.0.1:8000/upload/
```

### Ask a question

`POST /ask`

- request body JSON:
```json
{
  "docId": "<docId>",
  "question": "What is this document about?"
}
```

Example:
```bash
curl.exe -H "Content-Type: application/json" -d "{\"docId\":\"<docId>\",\"question\":\"Summarize the document.\"}" http://127.0.0.1:8000/ask/
```

### Health checks

- `GET /health/weaviate`
- `GET /health/llm`

## 4. Expected behavior

- If `WEAVIATE_URL` is configured and reachable, vectors are stored in Weaviate.
- If Weaviate is unavailable, the app will fall back to local storage.
- If `GEMINI_API_URL` and/or `GEMINI_API_KEY` are configured, LLM generation is attempted.
- Otherwise the `/ask` endpoint returns a fallback text response.

## 5. Troubleshooting

### Upload fails or hangs

- Verify the file path exists.
- Use an absolute path for `curl.exe` or PowerShell upload.
- Confirm the FastAPI server is running on port `8000`.

### Weaviate health reports local fallback

- Make sure `WEAVIATE_URL` points to your running Weaviate instance.
- Make sure `WEAVIATE_API_KEY` is set when your Weaviate requires auth.
- Validate the endpoint with:
```bash
curl http://<WEAVIATE_URL>/v1/.well-known/ready
```

### LLM returns fallback answer

- Set `GEMINI_API_URL` and `GEMINI_API_KEY`, or
- Set `GEMINI_PROJECT` and `GEMINI_API_KEY` for Vertex Predict.

## 6. Notes

- `requirements.txt` includes the runtime dependencies.
- The project uses a simple local embedding adapter and can be extended with a more advanced model.
- The readme is intentionally platform-neutral and supports Windows, macOS, and Linux.
