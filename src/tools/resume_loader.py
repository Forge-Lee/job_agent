from pathlib import Path


def extract_text_from_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages).strip()

def extract_text_from_docx(path: Path) -> str:
    from docx import Document

    document = Document(str(path))
    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs).strip()

def load_resume_text(resume_path: str) -> str:
    path = Path(resume_path)

    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        text = extract_text_from_pdf(path)

    elif suffix == ".docx":
        text = extract_text_from_docx(path)

    elif suffix == ".txt":
        text = path.read_text(encoding="utf-8")

    else:
        raise ValueError(f"Unsupported resume file type: {suffix}")
    
    if len(text.strip()) < 100:
        raise ValueError(
            "Extracted resume text is too short. The file may be scanned, image-based, or unreadable."
        )
    return text