import os
import openai
from typing import List, Dict

MODEL_DEFAULT = "gpt-3.5-turbo"

def setup_api_key_from_env():
    key = os.getenv("OPENAI_API_KEY")
    openai.api_key = key
    return bool(key)

def chat_call(messages: List[Dict], model: str = MODEL_DEFAULT, max_tokens: int = 1024, temperature: float = 0.2):
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return resp["choices"][0]["message"]["content"].strip()
