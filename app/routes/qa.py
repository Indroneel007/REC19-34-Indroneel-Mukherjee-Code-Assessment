from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.libs.retriever import get_topk_contexts
from app.libs.llm_adapter import generate_answer

router = APIRouter()

class AskRequest(BaseModel):
    docId: str
    question: str
    topK: int = 5

@router.post('/')
async def ask(req: AskRequest):
    if not req.docId or not req.question:
        raise HTTPException(status_code=400, detail='docId and question required')
    contexts = await get_topk_contexts(req.docId, req.question, req.topK)
    answer = await generate_answer(contexts, req.question)
    return {"answer": answer, "sources": [{"id": c['id'], "score": c['score']} for c in contexts]}
