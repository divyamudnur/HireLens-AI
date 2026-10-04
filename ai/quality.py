"""
HireLens AI – Resume Quality Indicator
=======================================
Provides a simple, deterministic signal about how reliably a resume
was parsed. Quality affects the confidence of skill extraction and
match scoring but does NOT block candidates from applying.

Quality Levels:
  GOOD    – Well-structured, text-rich PDF. Scores are reliable.
  LIMITED – Short or sparse PDF. Scores may be approximate.
  POOR    – Very short, empty, or likely scanned. Scores unreliable.
"""
from ai.text_processor import extract_skills


# Thresholds (tunable)
GOOD_WORD_COUNT    = 150   # words
LIMITED_WORD_COUNT = 40    # words
GOOD_CHAR_COUNT    = 800   # characters
LIMITED_CHAR_COUNT = 200   # characters
GOOD_SKILL_COUNT   = 3     # distinct matched skills


def assess_resume_quality(
    parse_success: bool,
    extracted_text: str,
    detected_skills: list[str] = None
) -> dict:
    """
    Assesses resume quality based on extraction signals.

    Parameters
    ----------
    parse_success   : bool – Whether the PDF was parsed without error.
    extracted_text  : str  – The raw text extracted from the PDF.
    detected_skills : list – Skills already detected (optional; re-extracted if None).

    Returns
    -------
    dict with keys:
      - level         : 'GOOD' | 'LIMITED' | 'POOR'
      - word_count    : int
      - char_count    : int
      - skill_count   : int
      - parse_success : bool
      - warning       : str | None  (user-facing advisory message)
      - icon          : str         (emoji indicator)
    """
    if not parse_success or not extracted_text or not extracted_text.strip():
        return {
            "level": "POOR",
            "word_count": 0,
            "char_count": 0,
            "skill_count": 0,
            "parse_success": parse_success,
            "warning": (
                "Limited resume text extracted. This may be a scanned image PDF "
                "or a corrupted file. Match score may be unreliable."
            ),
            "icon": "🔴"
        }

    text = extracted_text.strip()
    words = text.split()
    word_count = len(words)
    char_count = len(text)

    if detected_skills is None:
        detected_skills = extract_skills(text)
    skill_count = len(detected_skills)

    # Determine level
    if (word_count >= GOOD_WORD_COUNT
            and char_count >= GOOD_CHAR_COUNT
            and skill_count >= GOOD_SKILL_COUNT):
        level = "GOOD"
        icon = "🟢"
        warning = None

    elif (word_count >= LIMITED_WORD_COUNT
          or char_count >= LIMITED_CHAR_COUNT):
        level = "LIMITED"
        icon = "🟡"
        warning = (
            "Limited resume text extracted. Match score may be approximate. "
            "Consider uploading a text-based PDF for best results."
        )

    else:
        level = "POOR"
        icon = "🔴"
        warning = (
            "Very little text was extracted from the resume. "
            "This may be a scanned image PDF. Match score may be unreliable."
        )

    return {
        "level": level,
        "word_count": word_count,
        "char_count": char_count,
        "skill_count": skill_count,
        "parse_success": parse_success,
        "warning": warning,
        "icon": icon
    }
