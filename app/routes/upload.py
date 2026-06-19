from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from app.libs.pdf_processor import process_pdf

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'
PDF_DIR = DATA_DIR / 'pdfs'
PDF_DIR.mkdir(parents=True, exist_ok=True)

@router.post('/')
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files supported')
    doc_id = str(uuid.uuid4())
    dest = PDF_DIR / f"{doc_id}.pdf"
    with dest.open('wb') as f:
        contents = await file.read()
        f.write(contents)
    # Process in background - for starter we'll process synchronously
    try:
        await process_pdf(str(dest), doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Processing error: {e}')
    return {"docId": doc_id, "status": "processed"}
