from app.libs.embeddings_adapter import embed_texts
from app.libs.weaviate_client import query_vectors

async def get_topk_contexts(doc_id, question, top_k=5):
    qvecs = await embed_texts([question])
    qvec = qvecs[0].tolist() if hasattr(qvecs[0], 'tolist') else qvecs[0]
    hits = await query_vectors(doc_id, qvec, top_k)
    return hits
