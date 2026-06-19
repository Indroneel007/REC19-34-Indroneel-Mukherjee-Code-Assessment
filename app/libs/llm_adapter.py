import os
import asyncio

# Placeholder LLM adapter. Configure GEMINI_API_URL or other provider if available.
GEMINI_URL = os.getenv('GEMINI_API_URL')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

async def generate_answer(contexts, question):
    prompt = build_prompt(contexts, question)
    if GEMINI_URL:
        response = await fake_network_call(prompt)
        if isinstance(response, dict) and 'answer' in response:
            return response['answer']
        return str(response)
    ctx = '\n---\n'.join([c['text'] for c in contexts[:5]])
    return f"Answer (fallback):\nContext:\n{ctx}\n\nQuestion:\n{question}\n\n(Provide GEMINI_API_URL to enable generation)"

async def fake_network_call(prompt):
    await asyncio.sleep(0.1)
    return {'answer': 'LLM endpoint not configured, this is a placeholder', 'prompt': prompt}

def build_prompt(contexts, question):
    ctx = '\n\n'.join([f"[{i}] {c['text']}" for i,c in enumerate(contexts)])
    return f"You are a helpful assistant. Use the following context to answer the question.\n\nContext:\n{ctx}\n\nQuestion:\n{question}\n\nAnswer concisely and cite chunks by their bracketed index." 
