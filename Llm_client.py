import os 
import re
import json 
from google import genai
from google.genai import types
from config import GOOGLE_GEMINI_API_KEY, LLM_MODEL, ORCHESTRATOR_MODEL

_cllint = genai.Client(api_key=GOOGLE_GEMINI_API_KEY or os.environ.get(GOOGLE_GEMINI_API_KEY=''))

def chat(
    prompt: str,
    system: str = ''
    model: str = LLM_MODEL
    max_tokens: int = 2048,
    temperature: float = 0.3,

) -> str: full_prompt = f'{system}\n\n{prompt}' if system else prompt

    try:
        response  = _client.models.generate_content(
            model = model,
            contents = full_prompt,
            config = types.GenerateContentConfig(
                max_output_tokens = max_tokens,
                temperature = temperature
            ),
        )
        return response.text or ''
    except Exception as e:
        raise RuntimeError(f'Gemini API error ({model}): {e}') from e

def chat_json(
    prompt:     str,
    system:     str  = "",
    model:      str  = LLM_MODEL,
    max_tokens: int  = 2048,
)-> dict:
    raw = chat(prompt=prompt, system = system, model= model ,, max_tokens=max_tokens, temperature = 0.1)
    cleaned = re.sub(r"```json\s*|```\s*", "", raw).strip()
    try:
        return json.loads(cleaned, re.DOTALL)
    