import json
from typing import Tuple, List, Dict

# def parse_quiz_json(raw: str) -> Tuple[List[Dict], List[Dict]]:
#     """
#     Attempt to extract JSON block and parse mcqs + flashcards.
#     Returns (mcqs, flashcards). If parsing fails, returns ([], [{'q':'Raw','a': raw}])
#     """
#     text = raw.strip()
#     try:
#         start = text.index("{")
#         end = text.rindex("}") + 1
#         json_text = text[start:end]
#         data = json.loads(json_text)
#         mcqs = data.get("mcqs", [])
#         flashcards = data.get("flashcards", [])
#         return mcqs, flashcards
#     except Exception:
#         # fallback: try to find a JSON-like substring
#         try:
#             # quick heuristic: find first '[' and last ']' for mcqs
#             return [], [{"q": "Raw output", "a": raw}]
#         except Exception:
#             return [], [{"q": "Raw output", "a": raw}]

# import json
# import re

# def parse_quiz_json(raw: str):
#     """
#     Safely extract and parse quiz and flashcard data from raw Gemini output.
#     """
#     # Try to extract JSON part only (ignore extra notes or markdown)
#     match = re.search(r'\{[\s\S]*\}', raw)
#     if not match:
#         return [], []

#     try:
#         data = json.loads(match.group(0))
#         mcqs = data.get("mcqs", [])
#         flashcards = data.get("flashcards", [])
#         return mcqs, flashcards
#     except json.JSONDecodeError:
#         # If still fails, attempt minimal cleanup
#         cleaned = match.group(0).replace("```json", "").replace("```", "")
#         try:
#             data = json.loads(cleaned)
#             mcqs = data.get("mcqs", [])
#             flashcards = data.get("flashcards", [])
#             return mcqs, flashcards
#         except Exception:
#             return [], []
# import json
# import re

# def parse_quiz_json(raw: str):
#     """
#     Safely extract and parse quiz and flashcard data from raw Gemini output.
#     Automatically repairs truncated or partially valid JSON.
#     """
#     # Extract the JSON-like portion only
#     match = re.search(r'\{[\s\S]*\}', raw)
#     if not match:
#         return [], []

#     json_part = match.group(0)
#     # Remove code block markers if present
#     json_part = json_part.replace("```json", "").replace("```", "").strip()

#     # Try parsing directly
#     try:
#         data = json.loads(json_part)
#         return data.get("mcqs", []), data.get("flashcards", [])
#     except json.JSONDecodeError:
#         # Try trimming to last complete closing bracket
#         last_brace = json_part.rfind("}")
#         if last_brace != -1:
#             json_part = json_part[:last_brace+1]
#         try:
#             data = json.loads(json_part)
#             return data.get("mcqs", []), data.get("flashcards", [])
#         except Exception:
#             # Fallback: extract partial MCQs if JSON too broken
#             mcqs, flashcards = [], []
#             pattern = r'"question"\s*:\s*"([^"]+)"[\s\S]*?"answer"\s*:\s*"([^"]+)"'
#             for q, a in re.findall(pattern, raw):
#                 mcqs.append({"question": q, "answer": a})
#             return mcqs, flashcards
import json
import re

def parse_quiz_json(raw_text: str):
    """
    Safely extracts and parses quiz and flashcard data from raw model output.
    This version is more robust against JSON truncation.
    """
    # 1. First, try to find and parse the entire JSON object
    match = re.search(r'\{[\s\S]*\}', raw_text)
    if match:
        json_str = match.group(0)
        try:
            data = json.loads(json_str)
            return data.get("mcqs", []), data.get("flashcards", [])
        except json.JSONDecodeError:
            # The JSON is malformed, likely truncated. Proceed to salvaging.
            pass

    # 2. If full parsing fails, salvage what we can. Let's try to get the MCQs.
    mcqs = []
    flashcards = []
    
    # Regex to specifically find the content of the "mcqs" array
    mcq_match = re.search(r'"mcqs"\s*:\s*(\[[\s\S]*?\])', raw_text, re.DOTALL)
    if mcq_match:
        mcq_str = mcq_match.group(1)
        try:
            # Try parsing just the MCQs array
            mcqs = json.loads(mcq_str)
        except json.JSONDecodeError:
            # If even this fails, the MCQ block itself is broken. Fallback below.
            pass

    # Regex for flashcards, less likely to succeed if truncated
    flashcard_match = re.search(r'"flashcards"\s*:\s*(\[[\s\S]*?\])', raw_text, re.DOTALL)
    if flashcard_match:
        flashcard_str = flashcard_match.group(1)
        try:
            flashcards = json.loads(flashcard_str)
        except json.JSONDecodeError:
            pass # Flashcards are often the truncated part, so we accept failure here.

    # 3. If we still have no MCQs, use a final fallback regex on the raw text
    if not mcqs:
        pattern = r'"question"\s*:\s*"([^"]+)"[\s\S]*?"answer"\s*:\s*"([^"]+)"'
        for q, a in re.findall(pattern, raw_text):
            mcqs.append({"question": q, "options": [], "answer": a})

    return mcqs, flashcards