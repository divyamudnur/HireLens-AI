import os
import pymupdf as fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> tuple[bool, str, str]:
    """
    Extracts plain text from a single or multi-page PDF file using PyMuPDF (fitz).
    Returns (success: bool, extracted_text: str, message: str)
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return False, "", "PDF file not found."

    if not pdf_path.lower().endswith('.pdf'):
        return False, "", "File is not a valid PDF format."

    try:
        doc = fitz.open(pdf_path)
        
        if doc.page_count == 0:
            doc.close()
            return False, "", "The PDF document contains no pages."

        full_text = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text:
                full_text.append(text)

        doc.close()

        extracted_str = "\n".join(full_text).strip()

        if not extracted_str:
            return False, "", "The PDF appears to be empty or contains scanned images without extractable text."

        return True, extracted_str, f"Successfully extracted text across {len(full_text)} page(s)."

    except fitz.FileDataError:
        return False, "", "Corrupted or invalid PDF file structure."
    except Exception as e:
        return False, "", f"Failed to extract text from PDF: {str(e)}"
