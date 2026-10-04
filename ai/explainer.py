"""
HireLens AI – Rule-Based Match Explainer
=========================================
Generates structured, human-readable match breakdowns for candidates and
recruiters.  All output is deterministic — no LLM required.

Scoring formula (categorized jobs):
  Final Score = 40% TF-IDF + 40% Required + 15% Preferred + 5% Bonus
"""


def generate_match_explanation(match_data: dict) -> str:
    """
    Generates a structured match explanation string (Markdown).
    Works for both categorized (Required/Preferred/Bonus) jobs and
    legacy uncategorized jobs.
    """
    score   = match_data.get("match_score", 0.0)
    sim     = match_data.get("similarity_score", 0.0)
    has_cat = match_data.get("has_categorized_skills", False)

    lines = []

    # Overall score badge
    if score >= 75.0:
        lines.append(f"### ✅ **{score}% Overall Match** — **STRONG MATCH**")
    elif score >= 55.0:
        lines.append(f"### 🎯 **{score}% Overall Match** — **GOOD MATCH**")
    elif score >= 35.0:
        lines.append(f"### ⚡ **{score}% Overall Match** — **PARTIAL MATCH**")
    else:
        lines.append(f"### ⚠️ **{score}% Overall Match** — **WEAK MATCH**")

    if has_cat:
        req   = match_data.get("required",  {})
        pref  = match_data.get("preferred", {})
        bonus = match_data.get("bonus",     {})
        crit  = match_data.get("critical_coverage", 0.0)

        lines.append("---")
        lines.append(f"**Critical Skill Coverage (Required):** `{crit}%`")

        # Skill count summary
        req_icon  = " ✓" if req.get("matched_count") == req.get("total_count") and req.get("total_count", 0) > 0 else ""
        lines.append(f"- **Required Skills:** `{req.get('matched_count', 0)}/{req.get('total_count', 0)}`{req_icon}")
        lines.append(f"- **Preferred Skills:** `{pref.get('matched_count', 0)}/{pref.get('total_count', 0)}`")
        lines.append(f"- **Bonus Skills:** `{bonus.get('matched_count', 0)}/{bonus.get('total_count', 0)}`")

        lines.append("---")

        # Required detail
        if req.get("total_count", 0) > 0:
            m_str   = ", ".join([f"`{s}`" for s in req.get("matched", [])]) or "None"
            gap_str = ", ".join([f"`{s}`" for s in req.get("missing", [])]) or "None"
            lines.append(f"**Matched Required Skills:** {m_str}")
            lines.append(f"**Missing Required Skills:** {gap_str}")

        # Preferred detail
        if pref.get("total_count", 0) > 0:
            m_str   = ", ".join([f"`{s}`" for s in pref.get("matched", [])]) or "None"
            gap_str = ", ".join([f"`{s}`" for s in pref.get("missing", [])]) or "None"
            lines.append(f"**Matched Preferred Skills:** {m_str}")
            lines.append(f"**Missing Preferred Skills:** {gap_str}")

        # Bonus detail
        if bonus.get("total_count", 0) > 0:
            m_str = ", ".join([f"`{s}`" for s in bonus.get("matched", [])]) or "None"
            lines.append(f"**Bonus Skills Matched:** {m_str}")

    else:
        # Legacy / uncategorized fallback
        matched = match_data.get("matched_skills", [])
        missing = match_data.get("missing_skills", [])

        if matched:
            lines.append("**Matched Skills ({n}):** ".format(n=len(matched))
                         + ", ".join([f"`{s}`" for s in matched]))
        else:
            lines.append("**Matched Skills:** No direct technical skill overlap detected.")

        if missing:
            lines.append("**Skill Gaps ({n}):** ".format(n=len(missing))
                         + ", ".join([f"`{s}`" for s in missing]))
        else:
            lines.append("**Skill Gaps:** None identified!")

    lines.append("")
    lines.append(f"*(Content TF-IDF Text Alignment: {sim}%)*")

    return "\n\n".join(lines)


def generate_candidate_feedback(match_data: dict) -> str:
    """
    Generates candidate-facing feedback after applying.
    Does NOT expose recruiter-only information (verification flags,
    other candidates' scores, or private employer data).
    """
    score   = match_data.get("match_score", 0.0)
    has_cat = match_data.get("has_categorized_skills", False)

    lines = []

    if score >= 75.0:
        lines.append(f"### ✅ Your Match Score: **{score}%** — Strong profile alignment!")
    elif score >= 55.0:
        lines.append(f"### 🎯 Your Match Score: **{score}%** — Good alignment.")
    elif score >= 35.0:
        lines.append(f"### ⚡ Your Match Score: **{score}%** — Partial alignment.")
    else:
        lines.append(f"### ⚠️ Your Match Score: **{score}%** — Limited alignment.")

    lines.append("---")

    if has_cat:
        req   = match_data.get("required",  {})
        pref  = match_data.get("preferred", {})

        if req.get("total_count", 0) > 0:
            lines.append("**Required Skill Coverage:**")
            if req.get("matched"):
                lines.append("- Matched: " + ", ".join([f"`{s}`" for s in req["matched"]]))
            if req.get("missing"):
                lines.append("- **Skill Gaps (Required):** "
                             + ", ".join([f"`{s}`" for s in req["missing"]]))
                lines.append("  *(Strengthening these would significantly improve your score.)*")

        if pref.get("total_count", 0) > 0:
            lines.append("**Preferred Skill Coverage:**")
            if pref.get("matched"):
                lines.append("- Matched: " + ", ".join([f"`{s}`" for s in pref["matched"]]))
            if pref.get("missing"):
                lines.append("- **Skill Gaps (Preferred):** "
                             + ", ".join([f"`{s}`" for s in pref["missing"]]))
                lines.append("  *(Adding these would further strengthen your application.)*")

        # Skills to strengthen — combine all gaps
        all_gaps = (req.get("missing", []) + pref.get("missing", []))
        if all_gaps:
            lines.append("---")
            lines.append("**Skills to Strengthen:** "
                         + ", ".join([f"`{s}`" for s in sorted(set(all_gaps))]))

    else:
        matched = match_data.get("matched_skills", [])
        missing = match_data.get("missing_skills", [])
        if matched:
            lines.append("**Matched Skills:** " + ", ".join([f"`{s}`" for s in matched]))
        if missing:
            lines.append("**Skill Gaps:** " + ", ".join([f"`{s}`" for s in missing]))
            lines.append("**Skills to Strengthen:** "
                         + ", ".join([f"`{s}`" for s in sorted(set(missing))]))

    return "\n\n".join(lines)
