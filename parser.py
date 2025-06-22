import docx
import spacy

# It's more efficient to load the spaCy model once
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading 'en_core_web_sm' model. This may take a moment.")
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

def extract_text_from_docx(file_path: str) -> str:
    """Extracts plain text from a .docx file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise IOError(f"Error reading DOCX file at {file_path}: {e}")

def parse_resume(resume_text: str) -> dict:
    """
    Parses the extracted resume text to identify sections and entities.
    This is a placeholder and needs to be implemented with your
    specific resume parsing logic.
    """
    # Placeholder implementation: You would use NLP (like spaCy) or regex
    # to find sections like skills, experience, education, etc.
    doc = nlp(resume_text)
    entities = [ent.text for ent in doc.ents if ent.label_ in {'ORG', 'PERSON', 'GPE'}]

    # This is a simplified example. A robust implementation would be more complex.
    return {
        'full_text': resume_text,
        'entities': entities,
        'skills': "Extracted skills from text",
        'experience': "Extracted experience from text",
        'education': "Extracted education from text"
    }
