"""
HireLens AI – Deterministic Resume Claim Verifier
===================================================
Performs lightweight, rule-based cross-checking of resume text to surface
potential inconsistencies for recruiter review.

IMPORTANT – Language Policy:
  This module NEVER accuses a candidate of lying, fraud, or deception.
  All flags are framed as "recruiter verification recommended" signals.
  Flags are advisory only and do NOT determine hiring outcomes.

Severity levels: LOW | MEDIUM | HIGH
"""
import re
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_years_mentioned(text: str) -> list[int]:
    """Extracts all plausible 4-digit calendar years (1980–2030) from text."""
    candidates = re.findall(r'\b(19[89]\d|20[012]\d)\b', text)
    return [int(y) for y in candidates]


def _extract_year_ranges(text: str) -> list[tuple[int, Optional[int]]]:
    """
    Extracts (start_year, end_year | None) employment-like date ranges.
    Handles 'YYYY – YYYY', 'YYYY - Present', 'YYYY to Present', etc.
    """
    # Pattern: YYYY(–/-/to)YYYY or YYYY(–/-/to)(Present|Current|Now)
    pattern = (
        r'\b(19[89]\d|20[012]\d)'
        r'\s*(?:–|—|-|to|until)'
        r'\s*'
        r'(19[89]\d|20[012]\d|[Pp]resent|[Cc]urrent|[Nn]ow)\b'
    )
    ranges = []
    for m in re.finditer(pattern, text):
        start = int(m.group(1))
        end_raw = m.group(2)
        if re.match(r'\d+', end_raw):
            end = int(end_raw)
        else:
            end = datetime.now().year  # treat Present as current year
        ranges.append((start, end))
    return ranges


def _skill_has_evidence(skill: str, text: str, skills_section_end: int) -> bool:
    """
    Returns True if the skill appears in the text OUTSIDE of obvious
    skills/expertise list sections (i.e., has contextual support).
    A rough heuristic: count occurrences in the body vs. a dedicate skill list.
    """
    pattern = re.escape(skill)
    occurrences = [m.start() for m in re.finditer(pattern, text, re.IGNORECASE)]
    # If skill appears more than once → likely used in context somewhere
    if len(occurrences) > 1:
        return True
    # If the single occurrence is after the skills-section boundary, consider
    # it contextual even if it's a list item
    if occurrences and skills_section_end > 0:
        if occurrences[0] > skills_section_end:
            return True
    return False


def _find_skills_section_end(text: str) -> int:
    """Returns approximate char offset where the Skills section ends."""
    # Look for common section headers that follow a skills section
    section_headers = [
        r'(?i)(experience|work history|employment|projects|education|certifications|achievements)',
    ]
    combined = '|'.join(section_headers)
    m = re.search(combined, text)
    return m.start() if m else len(text) // 3  # default: first third


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def verify_resume_claims(
    resume_text: str,
    resume_skills: list[str] = None
) -> list[dict]:
    """
    Analyses resume text for potential unsupported or inconsistent claims.

    Returns a list of flag dicts, each containing:
      - type        : str   (category label)
      - explanation : str   (human-readable description)
      - evidence    : str   (excerpt or supporting data, if available)
      - severity    : str   (LOW | MEDIUM | HIGH)

    Returns an empty list for clean / inconsistency-free resumes.
    """
    if not resume_text or not resume_text.strip():
        return []

    flags: list[dict] = []
    text = resume_text

    # ── A. Skill claims without supporting evidence ─────────────────────────
    if resume_skills:
        skills_section_end = _find_skills_section_end(text)
        for skill in resume_skills:
            if not _skill_has_evidence(skill, text, skills_section_end):
                flags.append({
                    "type": "Unsupported Skill Claim",
                    "explanation": (
                        f"'{skill}' appears in the extracted skills but has limited "
                        "supporting evidence in the resume body (projects, experience, "
                        "or descriptions). Recruiter verification recommended."
                    ),
                    "evidence": f"Skill listed: {skill}",
                    "severity": "LOW"
                })

    # ── B. Overlapping employment periods ───────────────────────────────────
    ranges = _extract_year_ranges(text)
    if len(ranges) >= 2:
        ranges_sorted = sorted(ranges, key=lambda x: x[0])
        for i in range(len(ranges_sorted) - 1):
            a_start, a_end = ranges_sorted[i]
            b_start, b_end = ranges_sorted[i + 1]
            # Overlap if b starts before a ends (with >1 year buffer to avoid
            # flagging legitimate part-time / consulting overlaps under 12 months)
            if b_start < a_end - 1:
                flags.append({
                    "type": "Potential Timeline Overlap",
                    "explanation": (
                        f"Two employment periods appear to overlap: "
                        f"{a_start}–{a_end} and {b_start}–{b_end}. "
                        "This may indicate concurrent roles (consulting, part-time) "
                        "or could warrant clarification. "
                        "Potential inconsistency detected — recruiter verification recommended."
                    ),
                    "evidence": f"Ranges: {a_start}–{a_end} overlaps {b_start}–{b_end}",
                    "severity": "MEDIUM"
                })

    # ── C. Experience claims vs. visible employment dates ───────────────────
    # Look for "X years of experience" type claims
    exp_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)'
    exp_matches = re.finditer(exp_pattern, text, re.IGNORECASE)
    years_in_text = _extract_years_mentioned(text)

    for m in exp_matches:
        claimed_years = int(m.group(1))
        if claimed_years > 1 and years_in_text:
            earliest = min(years_in_text)
            latest = max(years_in_text)
            span = latest - earliest
            # Flag if claimed experience significantly exceeds visible date span
            if claimed_years > span + 3:
                flags.append({
                    "type": "Experience Timeline Inconsistency",
                    "explanation": (
                        f"Resume claims {claimed_years} years of experience, but the "
                        f"visible date range spans approximately {span} years "
                        f"({earliest}–{latest}). This may reflect omitted roles, "
                        "freelance work, or an imprecise claim. "
                        "Potential inconsistency detected — recruiter verification recommended."
                    ),
                    "evidence": (
                        f"Claimed: {claimed_years} yrs | "
                        f"Detected date range: {earliest}–{latest} ({span} yrs)"
                    ),
                    "severity": "MEDIUM" if claimed_years > span + 5 else "LOW"
                })
            break  # Flag at most once for experience claims

    # ── D. Education / timeline inconsistencies ─────────────────────────────
    # Degree claim with no graduation year visible
    degree_pattern = r'\b(Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?E\.?|M\.?E\.?|MBA)\b'
    degree_match = re.search(degree_pattern, text, re.IGNORECASE)
    if degree_match and not years_in_text:
        flags.append({
            "type": "Education Timeline Gap",
            "explanation": (
                "A degree is mentioned but no graduation year or date information "
                "could be identified in the resume. Recruiter verification recommended."
            ),
            "evidence": f"Degree keyword: '{degree_match.group(0)}'",
            "severity": "LOW"
        })

    # De-duplicate flags by type + evidence to avoid repeated LOW warnings
    seen = set()
    unique_flags = []
    for f in flags:
        key = (f["type"], f["evidence"])
        if key not in seen:
            seen.add(key)
            unique_flags.append(f)

    return unique_flags


def get_verification_summary(flags: list[dict]) -> dict:
    """
    Returns a concise summary of verification flags for display.

    Keys returned:
      - total_flags : int
      - high_count  : int
      - medium_count: int
      - low_count   : int
      - has_concerns: bool
      - headline    : str  (recruiter-facing status message)
    """
    if not flags:
        return {
            "total_flags": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "has_concerns": False,
            "headline": "No inconsistencies detected."
        }

    high   = sum(1 for f in flags if f["severity"] == "HIGH")
    medium = sum(1 for f in flags if f["severity"] == "MEDIUM")
    low    = sum(1 for f in flags if f["severity"] == "LOW")

    if high > 0:
        headline = "Verification Recommended — potential inconsistencies detected."
    elif medium > 0:
        headline = "Recruiter verification recommended for flagged items."
    else:
        headline = "Minor items noted — verification at recruiter discretion."

    return {
        "total_flags": len(flags),
        "high_count": high,
        "medium_count": medium,
        "low_count": low,
        "has_concerns": (high + medium) > 0,
        "headline": headline
    }
