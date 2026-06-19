from fastapi import APIRouter
from app.libs import weaviate_client
from app.libs.llm_adapter import generate_answer

router = APIRouter()

@router.get('/weaviate')
async def weaviate_health():
    status = weaviate_client.check_health()
    return status

@router.get('/llm')
async def llm_health():
    # simple smoke call
    try:
        ans = await generate_answer([{"id":"health","text":"test"}], "Say hello.")
        return {"llm": "ok", "sample": ans}
    except Exception as e:
        return {"llm": "error", "detail": str(e)}
