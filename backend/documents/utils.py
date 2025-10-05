import fitz
import docx

def extract_text_from_pdf(file_obj):
    try:
        pdf = fitz.open(stream=file_obj.read(), filetype="pdf")
        pages = []
        for i, page in enumerate(pdf, start=1):
            text = page.get_text()
            pages.append({"page": i, "text": text})
        pdf.close()
        return pages
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(file_obj):
    try:
        doc = docx.Document(file_obj)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return [{"page": 1, "text": text}]  # Treat as single page
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")
