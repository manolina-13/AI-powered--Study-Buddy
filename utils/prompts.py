from typing import List, Dict

def summary_prompt(text: str, style: str = "short") -> List[Dict]:
    if style == "short":
        instr = "Summarize the following text in 3-5 concise sentences."
    elif style == "bullet":
        instr = "Summarize the following text into 6-12 bullet points highlighting key concepts and definitions."
    else:
        instr = "Provide a detailed summary (approximately 200-300 words) of the following text, keeping technical accuracy."
    prompt = f"""{instr}

Text:
\"\"\"
{text}
\"\"\""""
    return [
        {"role": "system", "content": "You are a helpful assistant that summarizes academic content accurately."},
        {"role": "user", "content": prompt}
    ]

def simplify_prompt(text: str, level: str = "easy") -> List[Dict]:
    if level == "easy":
        instr = "Explain the following text in very simple language as if explaining to a 12-year-old. Use analogies and short sentences."
    else:
        instr = "Explain the following text in clear, concise college-level language suitable for first-year undergraduates."
    prompt = f"""{instr}

Text:
\"\"\"
{text}
\"\"\""""
    return [
        {"role": "system", "content": "You are a helpful teacher who explains technical topics in simple language."},
        {"role": "user", "content": prompt}
    ]

def quiz_prompt(text: str, num_mcq: int = 5) -> List[Dict]:
    prompt = f"""Given the following text, generate {num_mcq} multiple-choice questions (MCQs) with 4 choices each and identify the correct answer. Then provide {num_mcq} short-answer flashcards with 'Question' and 'Answer' pairs. Keep MCQs clear, non-tricky, and directly based on the text.

Text:
\"\"\"
{text}
\"\"\"
Format your response as JSON exactly like:
{{
  "mcqs":[
    {{"question":"...","options":["A...","B...","C...","D..."],"answer":"C"}},
    ...
  ],
  "flashcards":[
    {{"q":"...","a":"..."}},
    ...
  ]
}}"""
    return [
        {"role": "system", "content": "You are an assistant that creates educational MCQs and flashcards accurately."},
        {"role": "user", "content": prompt}
    ]
