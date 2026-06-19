import os
import asyncio
import requests

# Read config
GEMINI_URL = os.getenv('GEMINI_API_URL')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_PROJECT = os.getenv('GEMINI_PROJECT')
GEMINI_LOCATION = os.getenv('GEMINI_LOCATION', 'us-central1')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'text-bison-001')


async def generate_answer(contexts, question):
    prompt = build_prompt(contexts, question)
    # Prefer explicit URL
    if GEMINI_URL and GEMINI_KEY:
        return await _call_url(GEMINI_URL, GEMINI_KEY, prompt)

    # Try Vertex AI Predict style endpoint if project and key present
    if GEMINI_PROJECT and GEMINI_KEY:
        vertex_url = f"https://{GEMINI_LOCATION}-aiplatform.googleapis.com/v1/projects/{GEMINI_PROJECT}/locations/{GEMINI_LOCATION}/models/{GEMINI_MODEL}:predict"
        try:
            return await _call_url(vertex_url, GEMINI_KEY, prompt, vertex=True)
        except Exception:
            pass

    # Final fallback (should not be used when proper creds are provided)
    ctx = '\n---\n'.join([c['text'] for c in contexts[:5]])
    return f"Answer (fallback):\nContext:\n{ctx}\n\nQuestion:\n{question}\n\n(Provide GEMINI_API_URL or valid project/key to enable generation)"


async def _call_url(url, key, prompt, vertex: bool = False):
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

    if vertex:
        payload = {"instances": [{"content": prompt}]}
    else:
        payload = {"prompt": prompt}

    # Use blocking requests in a thread to keep async signature
    def do_request():
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    resp_json = await asyncio.to_thread(do_request)

    # Try to extract text from common response shapes
    # Vertex AI predict: resp_json.get('predictions', [])[0].get('content')
    if isinstance(resp_json, dict):
        # Check Vertex-like responses
        preds = resp_json.get('predictions')
        if preds and isinstance(preds, list):
            first = preds[0]
            if isinstance(first, dict):
                for key_opt in ('content', 'text', 'output'):
                    if key_opt in first:
                        return first[key_opt]
        # Check for 'candidates' field (Generative API)
        candidates = resp_json.get('candidates')
        if candidates and isinstance(candidates, list):
            c0 = candidates[0]
            if isinstance(c0, dict) and 'content' in c0:
                return c0['content']
        # Check for top-level answer keys
        for k in ('answer', 'output', 'text'):
            if k in resp_json and isinstance(resp_json[k], str):
                return resp_json[k]

    # Last resort: return full JSON string
    return str(resp_json)


def build_prompt(contexts, question):
    ctx = '\n\n'.join([f"[{i}] {c['text']}" for i, c in enumerate(contexts)])
    return f"You are a helpful assistant. Use the following context to answer the question.\n\nContext:\n{ctx}\n\nQuestion:\n{question}\n\nAnswer concisely and cite chunks by their bracketed index." 
