import io
import docx2txt
from pypdf import PdfReader

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extracts plain text from a PDF, DOCX, or TXT file blazing fast."""
    text = ""
    
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                    
    elif filename.lower().endswith((".doc", ".docx")):
        # docx2txt expects a file-like object
        text = docx2txt.process(io.BytesIO(file_bytes))
        
    else:
        # Assume it might be plain text
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            text = ""
            
    return text.strip()
