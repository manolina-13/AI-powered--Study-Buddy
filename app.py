"""
Main Streamlit app for AI-Powered Study Buddy (Gemini API)
Run:
    pip install -r requirements.txt
    pip install google-generativeai
    $env:GEMINI_API_KEY="your_actual_gemini_api_key_here"  # Windows PowerShell
    streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import google.generativeai as genai
import docx
import PyPDF2
import json

# --- Utility Functions (Normally in separate files) ---

def read_uploaded_file(uploaded_file):
    """Reads content from an uploaded file (.pdf, .docx, .txt)."""
    if uploaded_file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
    elif uploaded_file.name.endswith(".docx"):
        try:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error reading DOCX: {e}"
    elif uploaded_file.name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"Error reading TXT: {e}"
    return "Unsupported file type."

def summary_prompt(text, style):
    """Generates a prompt for summarizing text."""
    return f"Summarize the following text in a {style} style. Keep the output to a few paragraphs at most:\n\n{text}"

def simplify_prompt(text, level):
    """Generates a prompt for simplifying text."""
    if level == "easy":
        return f"Explain the following text in simple terms, like I'm a beginner. Keep the explanation concise, around a couple of paragraphs:\n\n{text}"
    else:
        return f"Explain the following text in a detailed, college-level manner. The explanation should be thorough but limited to a few paragraphs:\n\n{text}"

def quiz_prompt(text, num_mcq):
    """Generates a prompt for creating a quiz."""
    return f"""
    Based on the text below, generate {num_mcq} multiple-choice questions (MCQs) and {num_mcq} flashcards (question/answer pairs).
    Return the output as a single, valid JSON object with two keys: "mcqs" and "flashcards".

    For "mcqs", each item should be an object with "question", "options" (a list of 4 strings), and "answer".
    For "flashcards", each item should be an object with "question" and "answer".

    Text:
    {text}
    """

def plan_prompt(text, duration):
    """Generates a prompt for creating a study plan."""
    return f"""
    Analyze the following text and create a structured study plan for a session of {duration}.
    The plan should break down the topics into manageable chunks for studying and revision.
    Include a 5-minute break for approximately every 45 minutes of study.
    Return the output as a single, valid JSON object. The root should be a list of dictionaries.
    Each dictionary in the list should represent a block in the schedule and must have the following keys:
    - "block_type": A string that is one of "study", "revision", or "break".
    - "title": A short, descriptive title for the block (e.g., "Introduction to Topic X", "Quick Recap", "Short Break").
    - "description": A one-sentence description of the task for that block.
    - "duration": An integer representing the time in minutes for the block.

    The sum of all durations should be close to the total session duration.

    Text:
    {text}
    """


def parse_quiz_json(raw_json_text):
    """Safely parses a JSON string that might be embedded in markdown."""
    try:
        json_start = raw_json_text.find('{')
        json_end = raw_json_text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            clean_json = raw_json_text[json_start:json_end]
            data = json.loads(clean_json)
            return data.get("mcqs", []), data.get("flashcards", [])
    except (json.JSONDecodeError, AttributeError) as e:
        st.error(f"Error parsing quiz JSON: {e}")
        st.write("Raw output from API:", raw_json_text)
    return [], []

def parse_plan_json(raw_json_text):
    """Safely parses a JSON list string that might be embedded in markdown."""
    try:
        json_start = raw_json_text.find('[')
        json_end = raw_json_text.rfind(']') + 1
        if json_start != -1 and json_end != -1:
            clean_json = raw_json_text[json_start:json_end]
            data = json.loads(clean_json)
            return data
    except (json.JSONDecodeError, AttributeError) as e:
        st.error(f"Error parsing study plan JSON: {e}")
        st.write("Raw output from API:", raw_json_text)
    return []


# --- Main Streamlit App ---

# Configure Gemini API key from environment
gemini_key = os.environ.get("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)
else:
    st.error("GEMINI_API_KEY not set. Set it in your environment before running.")
    st.stop()


def call_gemini(prompt_text, max_tokens=4096, temperature=0.4):
    """Calls the Gemini API and handles responses without valid content."""
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(
            prompt_text,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        if response.parts:
            return response.text
        else:
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            return f"Error calling Gemini API: No content returned. Finish reason: {finish_reason}"
    except Exception as e:
        return f"Error calling Gemini API: {e}"


# Page config
st.set_page_config(page_title="AI Study Buddy", layout="wide")
st.title("📚LearnEd - AI Powered Study Buddy")

# Sidebar: Inputs
with st.sidebar:
    st.header("💡 Get Started")
    st.info("Upload your study notes or paste any text to activate the Study Buddy!")
    
    st.header("Input & Options")
    uploaded_file = st.file_uploader("Upload notes (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
    paste_text = st.text_area("Or paste text/topic here", height=200)
    st.markdown("---")
    
    st.header("Actions & Settings")
    st.subheader("Summary options")
    summary_style = st.selectbox("Style", ["short", "bullet points", "detailed"])
    st.subheader("Simplify / Explain")
    explain_level = st.selectbox("Level", ["simple", "college-level"])
    st.subheader("Quiz & Flashcards")
    num_mcq = st.slider("Number of MCQs/Flashcards", 3, 10, 5)
    st.subheader("Study Session Plan")
    study_duration = st.selectbox(
        "Session duration",
        ["30 minutes", "1 hour", "1.5 hours", "2 hours", "2.5 hours", "3 hours"]
    )


# Prepare input text
full_text = ""
if uploaded_file:
    full_text = read_uploaded_file(uploaded_file)
    st.sidebar.write("Uploaded:", uploaded_file.name)
elif paste_text:
    full_text = paste_text


# --- CONDITIONAL MAIN CONTENT AREA ---

# If no text is provided, show the welcome page.
if not full_text.strip():
    st.header("Welcome!")
    st.markdown("""
        This assistant is designed to supercharge your study sessions. It can help you summarize complex documents, 
        explain difficult concepts, test your knowledge, and even create a structured study plan.
    """)
    
    st.markdown("### How to use LearnEd:")
    st.markdown("""
        1.  **Upload a file** or **paste your text** in the sidebar on the left.
        2.  Once your text is loaded, you will see a preview.
        3.  **Choose your favorite tool** to summarize, explain, quiz yourself, or plan your session!
    """)
    
    st.info("Just enter your study material in the sidebar to get started.")
    
    # A decorative image for the welcome page
    st.image(
        "https://images.pexels.com/photos/4144179/pexels-photo-4144179.jpeg",
        caption="Photo by Julia M Cameron from Pexels"
    )

# If text IS provided, show the main application interface.
else:
    st.header("1. Your Study Material")
    if uploaded_file and not full_text.strip():
        st.error("Could not extract text from the uploaded PDF. The file might be image-based or corrupted.")
    else:
        st.text_area("Preview (first 60k chars)", value=full_text[:60000], height=250, disabled=True)

    # Initialize session_state for all outputs
    if 'mcqs' not in st.session_state:
        st.session_state.mcqs = []
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    if 'summary' not in st.session_state:
        st.session_state.summary = ""
    if 'explanation' not in st.session_state:
        st.session_state.explanation = ""
    if 'study_plan' not in st.session_state:
        st.session_state.study_plan = []

    # Action Buttons
    st.markdown("### 2. Choose an Action")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("🔍 Summarize", use_container_width=True):
            with st.spinner("Summarizing..."):
                st.session_state.clear() # Clear all old state
                prompt = summary_prompt(full_text, style=summary_style)
                st.session_state.summary = call_gemini(prompt)

    with c2:
        if st.button("🧑‍🏫 Simplify / Explain", use_container_width=True):
            with st.spinner("Generating explanation..."):
                st.session_state.clear()
                prompt = simplify_prompt(full_text, level=explain_level)
                st.session_state.explanation = call_gemini(prompt)

    with c3:
        if st.button("📝 Generate Quiz", use_container_width=True):
            with st.spinner("Generating quiz & flashcards..."):
                st.session_state.clear()
                prompt = quiz_prompt(full_text, num_mcq=num_mcq)
                raw_quiz_data = call_gemini(prompt)
                mcqs, flashcards = parse_quiz_json(raw_quiz_data)
                st.session_state.mcqs = mcqs
                st.session_state.flashcards = flashcards

    with c4:
        if st.button("🗓️ Plan Session", use_container_width=True):
            with st.spinner("Creating your study plan..."):
                st.session_state.clear()
                prompt = plan_prompt(full_text, duration=study_duration)
                raw_plan_data = call_gemini(prompt)
                st.session_state.study_plan = parse_plan_json(raw_plan_data)


    # --- Display Logic (Full Width) ---

    if st.session_state.get("summary"):
        st.success("Summary ready!")
        st.markdown("### Summary")
        st.write(st.session_state.summary)
        st.download_button("Download Summary", st.session_state.summary, file_name="summary.txt")
        st.markdown("---")

    if st.session_state.get("explanation"):
        st.success("Explanation ready!")
        st.markdown("### Simplified Explanation")
        st.write(st.session_state.explanation)
        st.download_button("Download Explanation", st.session_state.explanation, file_name="explanation.txt")
        st.markdown("---")

    if st.session_state.get("study_plan"):
        st.success("Study plan generated!")
        st.markdown("### Your Study Session Plan")
        for i, block in enumerate(st.session_state.study_plan):
            is_done = st.checkbox(f"Mark as Done", key=f"plan_item_{i}", value=False)
            
            block_type = block.get("block_type", "study").lower()
            title = block.get("title", "Untitled")
            desc = block.get("description", "No description.")
            duration = block.get("duration", 0)
            
            style = 'opacity: 0.4; text-decoration: line-through;' if is_done else ''
            
            if block_type == 'study':
                icon = "📚"
            elif block_type == 'revision':
                icon = "🔄"
            elif block_type == 'break':
                icon = "☕"
            else:
                icon = "✏️"

            with st.container(border=True):
                st.markdown(
                    f'<div style="{style}">'
                    f'<h4>{icon} {title}</h4>'
                    f'<b>🕰️ Duration: {duration} minutes</b>'
                    f'<p>{desc}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        st.markdown("---")

    if st.session_state.get("mcqs"):
        st.success("Quiz & flashcards generated!")
        st.markdown("### Multiple-Choice Questions")
        for i, m in enumerate(st.session_state.mcqs, start=1):
            st.write(f"**Q{i}: {m.get('question')}**")
            opts = m.get("options", [])
            user_answer = st.radio("Options:", opts, key=f"mcq_{i}", index=None, label_visibility="collapsed")
            if st.button(f"Show Answer for Q{i}", key=f"ans_btn_{i}"):
                st.info(f"Correct Answer: {m.get('answer')}")
            st.markdown("---")

    if st.session_state.get("flashcards"):
        st.markdown("### Flashcards")
        df = pd.DataFrame(st.session_state.flashcards)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Flashcards (CSV)", csv, file_name="flashcards.csv")
    
st.caption("Built with ❤️ - AI Study Buddy | Designed and Developed by Manolina Das")
