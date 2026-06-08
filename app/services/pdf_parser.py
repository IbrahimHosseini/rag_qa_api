
import pdfplumber

def pdf_parser(path: str) -> list[tuple[int, str]]:
    pages = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append((i+1, text.strip()))
    
    return pages