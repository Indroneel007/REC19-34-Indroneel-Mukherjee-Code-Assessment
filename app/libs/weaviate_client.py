import os
import json
from app.db import load_vectors

WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not WEAVIATE_URL:
        return None
    try:
        import weaviate
        if WEAVIATE_API_KEY:
            auth = weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)
            _client = weaviate.Client(url=WEAVIATE_URL, auth_client_secret=auth)
        else:
            _client = weaviate.Client(url=WEAVIATE_URL)
        return _client
    except Exception:
        return None


async def upsert_vectors(items):
    client = _get_client()
    if client:
        schema = {
            'class': 'DocumentChunk',
            'vectorizer': 'none',
            'properties': [
                {'name': 'text', 'dataType': ['text']},
                {'name': 'metadata', 'dataType': ['text']}
            ]
        }
        try:
            classes = [c['class'] for c in client.schema.get().get('classes', [])]
            if 'DocumentChunk' not in classes:
                client.schema.create_class(schema)
        except Exception:
            pass
        batch = client.batch
        with batch as b:
            for it in items:
                obj = {'text': it['text'], 'metadata': str(it['metadata'])}
                b.add_data_object(obj, 'DocumentChunk', uuid=it['id'], vector=it['vector'])
        return
    doc_id = items[0]['metadata'].get('docId') if items else 'fallback'
    existing = load_vectors(doc_id) or []
    existing.extend(items)
    return


import math


def _cosine(a, b):
    da = sum(x * x for x in a)
    db = sum(x * x for x in b)
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(da) * math.sqrt(db) + 1e-10)


async def query_vectors(doc_id, vector, top_k=5):
    client = _get_client()
    if client:
        try:
            vec_list = ','.join([str(float(x)) for x in vector])
            query = f"{{Get{{DocumentChunk(nearVector:{{vector:[{vec_list}]}} , limit:{top_k}){{id text _additional{{distance}}}}}}}}"
            resp = client.query.raw(query)
            hits = resp['data']['Get']['DocumentChunk']
            return [{'id': h['id'], 'text': h['text'], 'score': 1 - h['_additional']['distance']} for h in hits]
        except Exception:
            pass
    store = load_vectors(doc_id) or load_vectors('fallback') or []
    scored = []
    for item in store:
        score = _cosine(vector, item['vector'])
        scored.append({'id': item['id'], 'text': item['text'], 'score': score})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_k]
