import hashlib

def _text_to_vector(text: str, dim: int = 384):
    data = hashlib.sha256(text.encode('utf-8')).digest()
    vec = [0.0] * dim
    for idx, byte in enumerate(data):
        vec[idx % dim] += byte / 255.0
    norm = sum(x * x for x in vec) ** 0.5
    if norm == 0:
        return vec
    return [x / norm for x in vec]

async def embed_texts(texts):
    return [_text_to_vector(text) for text in texts]
