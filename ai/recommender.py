"""
HireLens AI – Recruiter Recommendation Engine
==============================================
Generates deterministic 'Why This Candidate?' summaries for recruiters.

Recommendation tiers (deterministic rules, no LLM):
  STRONG MATCH  – score >= 75 AND critical_coverage >= 80
  GOOD MATCH    – score >= 55 AND critical_coverage >= 50
  PARTIAL MATCH – score >= 35
  WEAK MATCH    – score < 35

IMPORTANT: These recommendations are recruiter DECISION SUPPORT only.
No automatic hiring or rejection decisions are made by this module.
"""
from ai.verifier import get_verification_summary


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STRONG_SCORE    = 75.0
STRONG_COVERAGE = 80.0
GOOD_SCORE      = 55.0
GOOD_COVERAGE   = 50.0
PARTIAL_SCORE   = 35.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_recommendation(match_data: dict, flags: list[dict] = None) -> dict:
    """
    Generates the full 'Why This Candidate?' recruiter package.

    Parameters
    ----------
    match_data : dict – Output from calculate_match_score().
    flags      : list – Output from verify_resume_claims() (optional).

    Returns
    -------
    dict with keys:
      - recommendation    : str  (STRONG MATCH | GOOD MATCH | PARTIAL MATCH | WEAK MATCH)
      - recommendation_color : str  (for UI display)
      - overall_score     : float
      - critical_coverage : float
      - top_strengths     : list[str]
      - critical_gaps     : list[str]
      - preferred_gaps    : list[str]
      - verification_summary : dict
      - recruiter_notes   : list[str]
    """
    if flags is None:
        flags = []

    score = match_data.get("match_score", 0.0)
    crit_cov = match_data.get("critical_coverage", 0.0)
    has_cat = match_data.get("has_categorized_skills", False)

    req  = match_data.get("required",  {"matched": [], "missing": [], "total_count": 0})
    pref = match_data.get("preferred", {"matched": [], "missing": [], "total_count": 0})
    bonus = match_data.get("bonus",    {"matched": [], "missing": [], "total_count": 0})

    # ── Recommendation tier ────────────────────────────────────────────────
    if score >= STRONG_SCORE and crit_cov >= STRONG_COVERAGE:
        recommendation = "STRONG MATCH"
        rec_color = "green"
    elif score >= GOOD_SCORE and crit_cov >= GOOD_COVERAGE:
        recommendation = "GOOD MATCH"
        rec_color = "blue"
    elif score >= PARTIAL_SCORE:
        recommendation = "PARTIAL MATCH"
        rec_color = "orange"
    else:
        recommendation = "WEAK MATCH"
        rec_color = "red"

    # ── Top Strengths ──────────────────────────────────────────────────────
    strengths = []
    if has_cat:
        if req["matched"]:
            strengths.append(
                f"Meets {len(req['matched'])}/{req['total_count']} required skills: "
                + ", ".join(req["matched"])
            )
        if pref["matched"]:
            strengths.append(
                f"Has {len(pref['matched'])} preferred skill(s): "
                + ", ".join(pref["matched"])
            )
        if bonus["matched"]:
            strengths.append(
                f"Bonus skills matched: " + ", ".join(bonus["matched"])
            )
    else:
        all_matched = match_data.get("matched_skills", [])
        if all_matched:
            strengths.append(f"Matched skills: " + ", ".join(all_matched[:6]))

    if score >= 70:
        strengths.append(f"Strong overall alignment ({score}%)")
    elif score >= 50:
        strengths.append(f"Moderate overall alignment ({score}%)")

    if not strengths:
        strengths.append("No significant skill matches identified.")

    # ── Critical Gaps ──────────────────────────────────────────────────────
    critical_gaps = req["missing"] if has_cat else []
    preferred_gaps = pref["missing"] if has_cat else match_data.get("missing_skills", [])

    # ── Recruiter Notes ────────────────────────────────────────────────────
    notes = []

    if has_cat and req["total_count"] > 0:
        if crit_cov == 100.0:
            notes.append("All required skills are present.")
        elif crit_cov >= 50.0:
            notes.append(
                f"Partial required skill coverage ({crit_cov}%). "
                "Consider whether the missing required skills are trainable."
            )
        else:
            notes.append(
                f"Low required skill coverage ({crit_cov}%). "
                "Significant required skills are absent."
            )

    if flags:
        vsummary = get_verification_summary(flags)
        if vsummary["has_concerns"]:
            notes.append(vsummary["headline"])
    else:
        vsummary = get_verification_summary([])

    notes.append(
        "This recommendation is recruiter decision support only. "
        "Final hiring decisions remain with the recruiter."
    )

    return {
        "recommendation": recommendation,
        "recommendation_color": rec_color,
        "overall_score": score,
        "critical_coverage": crit_cov,
        "top_strengths": strengths,
        "critical_gaps": critical_gaps,
        "preferred_gaps": preferred_gaps,
        "verification_summary": vsummary,
        "recruiter_notes": notes
    }
