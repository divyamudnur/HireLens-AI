import re
from utils.constants import SKILL_KEYWORDS

def clean_text(text: str) -> str:
    """
    Normalizes raw text extracted from PDF:
    - Removes non-printable control characters
    - Collapses multiple whitespace/newlines into clean spacing
    - Preserves meaningful punctuation and casing
    """
    if not text:
        return ""

    # Remove non-printable control characters except newline
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
    
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace multiple newlines with maximum double newline
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    return text.strip()

def extract_skills(text: str, skill_list: list[str] = None) -> list[str]:
    """
    Extracts matched technical skills from text using robust boundary regex matching.
    Handles special characters safely (e.g. C++, C#, React.js, REST API).
    """
    if not text:
        return []

    if skill_list is None:
        skill_list = SKILL_KEYWORDS

    detected_skills = set()

    for skill in skill_list:
        skill_clean = skill.strip()
        if not skill_clean:
            continue

        escaped_skill = re.escape(skill_clean)
        
        # Match with boundary symbols: start/end of line, spaces, or standard delimiters
        # Boundary includes period/exclamation/question so skills at sentence end are matched
        pattern = r'(?:^|[\s,;:()\/\-\[\]\n\r])' + escaped_skill + r'(?=$|[\s,;:.!?()\/\-\[\]\n\r])'

        if re.search(pattern, text, re.IGNORECASE):
            detected_skills.add(skill_clean)

    return sorted(list(detected_skills), key=lambda x: x.lower())

def process_resume_text(raw_text: str) -> dict:
    """
    Processes raw extracted text and returns structured metrics & extracted skills.
    """
    cleaned = clean_text(raw_text)
    skills = extract_skills(cleaned)
    words = cleaned.split()

    return {
        "cleaned_text": cleaned,
        "detected_skills": skills,
        "word_count": len(words),
        "char_count": len(cleaned)
    }
