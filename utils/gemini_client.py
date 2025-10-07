"""
Gemini client wrapper for AI Study Buddy
Provides same interface as openai_client for easy replacement
"""

import os
import google.generativeai as genai

def setup_api_key_from_env():
    """
    Reads GEMINI_API_KEY from environment and configures the client.
    Returns True if key exists, False otherwise.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def chat_call(messages, max_tokens=500, temperature=0.2):
    """
    Accepts a list of messages in OpenAI style: [{"role":"user","content":"..."}]
    Returns the generated text from Gemini API
    """
    try:
        # Combine messages into a single prompt
        prompt_text = "\n".join([m["content"] for m in messages])
        response = genai.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"
