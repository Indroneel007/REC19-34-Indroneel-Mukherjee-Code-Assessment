import json
from pypdf import PdfReader
from app.libs.splitter import split_text
from app.libs.embeddings_adapter import embed_texts
from app.libs.weaviate_client import upsert_vectors
from app.db import save_metadata, save_vectors

# Process PDF synchronously so upload can delegate it cleanly.
def process_pdf(file_path: str, doc_id: str):
    reader = PdfReader(file_path)
    text = []
    for p in reader.pages:
        try:
            text.append(p.extract_text() or '')
        except Exception:
            text.append('')
    full = '\n'.join(text)
    chunks = split_text(full)
    chunk_objs = [{"id": f"{doc_id}_chunk_{i}", "text": c, "index": i} for i, c in enumerate(chunks)]
    save_metadata(doc_id, {"filePath": file_path, "chunks": len(chunk_objs)})
    texts = [c['text'] for c in chunk_objs]
    vectors = embed_texts(texts)
    items = []
    for i, c in enumerate(chunk_objs):
        vector = vectors[i].tolist() if hasattr(vectors[i], 'tolist') else vectors[i]
        items.append({
            "id": c['id'],
            "text": c['text'],
            "metadata": {"docId": doc_id, "index": c['index']},
            "vector": vector,
        })
    upsert_vectors(items)
    save_vectors(doc_id, items)
    return True
