from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, qa, health

load_dotenv()

app = FastAPI(title="PDF RAG Starter (Python)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload")
app.include_router(qa.router, prefix="/ask")
app.include_router(health.router, prefix="/health")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(__import__('os').environ.get('PORT', 8000)), reload=True)
