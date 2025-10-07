import io
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)

def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as buf:
        doc = docx.Document(buf)
        paras = [p.text for p in doc.paragraphs]
    return "\n".join(paras)

def extract_text_from_txt_bytes(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return file_bytes.decode("latin-1", errors="ignore")

def read_uploaded_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    if name.endswith(".pdf"):
        return extract_text_from_pdf_bytes(raw)
    elif name.endswith(".docx"):
        return extract_text_from_docx_bytes(raw)
    elif name.endswith(".txt"):
        return extract_text_from_txt_bytes(raw)
    else:
        # fallback try to decode
        try:
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return str(raw)
