from ai.matcher import compute_cosine_similarity
from ai.text_processor import extract_skills


def parse_skill_list(skill_input) -> list[str]:
    """Helper to convert string/list into a clean list of unique skills."""
    if not skill_input:
        return []
    if isinstance(skill_input, str):
        parts = [p.strip() for p in skill_input.replace('\n', ',').split(',') if p.strip()]
        return extract_skills(" ".join(parts), skill_list=parts) or parts
    elif isinstance(skill_input, list):
        return [str(s).strip() for s in skill_input if str(s).strip()]
    return []


def calculate_match_score(
    resume_text: str,
    jd_text: str,
    resume_skills: list[str] = None,
    jd_skills: list[str] = None,
    required_skills: list[str] | str = None,
    preferred_skills: list[str] | str = None,
    bonus_skills: list[str] | str = None
) -> dict:
    """
    Calculates deterministic 0-100 match score.

    Specification formula (categorized jobs):
      Final Score = 40pct TF-IDF similarity
                  + 40pct Required Skill Coverage
                  + 15pct Preferred Skill Coverage
                  +  5pct Bonus Skill Coverage

    Legacy fallback (uncategorized jobs): 70pct skill overlap + 30pct TF-IDF.
    Division-by-zero protected throughout.
    """
    if not resume_text or not jd_text or not resume_text.strip() or not jd_text.strip():
        return {
            "match_score": 0.0,
            "similarity_score": 0.0,
            "skill_score": 0.0,
            "critical_coverage": 0.0,
            "has_categorized_skills": False,
            "required": {"matched": [], "missing": [], "total_count": 0, "matched_count": 0, "pct": 0.0},
            "preferred": {"matched": [], "missing": [], "total_count": 0, "matched_count": 0, "pct": 0.0},
            "bonus": {"matched": [], "missing": [], "total_count": 0, "matched_count": 0, "pct": 0.0},
            "matched_skills": [],
            "missing_skills": [],
            "jd_skills": []
        }

    # 1. TF-IDF Cosine Similarity (0.0 to 100.0)
    cos_sim = compute_cosine_similarity(resume_text, jd_text)
    similarity_percentage = cos_sim * 100.0

    # 2. Extract resume skills
    if resume_skills is None:
        resume_skills = extract_skills(resume_text)

    resume_lower_map = {s.lower(): s for s in resume_skills}

    # Parse category inputs
    req_parsed = parse_skill_list(required_skills)
    pref_parsed = parse_skill_list(preferred_skills)
    bonus_parsed = parse_skill_list(bonus_skills)

    has_categorized = bool(req_parsed or pref_parsed or bonus_parsed)

    def evaluate_category(cat_skills):
        """Returns coverage info for one skill category. Empty -> pct=100.0 (no penalty)."""
        if not cat_skills:
            return {"matched": [], "missing": [], "total_count": 0, "matched_count": 0, "pct": 100.0}
        cat_map = {s.lower(): s for s in cat_skills}
        matched_keys = set(cat_map.keys()).intersection(set(resume_lower_map.keys()))
        missing_keys = set(cat_map.keys()) - set(resume_lower_map.keys())
        matched_list = sorted([cat_map[k] for k in matched_keys])
        missing_list = sorted([cat_map[k] for k in missing_keys])
        pct = (len(matched_keys) / len(cat_map)) * 100.0
        return {
            "matched": matched_list,
            "missing": missing_list,
            "total_count": len(cat_map),
            "matched_count": len(matched_list),
            "pct": round(pct, 1)
        }

    req_eval = evaluate_category(req_parsed)
    pref_eval = evaluate_category(pref_parsed)
    bonus_eval = evaluate_category(bonus_parsed)

    critical_coverage = req_eval["pct"] if req_eval["total_count"] > 0 else 0.0

    if has_categorized:
        # Specification formula: 40pct TF-IDF + 40pct Required + 15pct Preferred + 5pct Bonus
        # Empty categories have weight redistributed proportionally.
        tfidf_weight = 0.40
        req_weight   = 0.40 if req_eval["total_count"]   > 0 else 0.0
        pref_weight  = 0.15 if pref_eval["total_count"]  > 0 else 0.0
        bonus_weight = 0.05 if bonus_eval["total_count"] > 0 else 0.0

        total_skill_weight = req_weight + pref_weight + bonus_weight

        if total_skill_weight > 0:
            skill_budget = 1.0 - tfidf_weight
            scale = skill_budget / total_skill_weight
            req_w_norm   = req_weight   * scale
            pref_w_norm  = pref_weight  * scale
            bonus_w_norm = bonus_weight * scale
        else:
            req_w_norm = pref_w_norm = bonus_w_norm = 0.0

        combined_raw = (
            tfidf_weight  * similarity_percentage
            + req_w_norm  * req_eval["pct"]
            + pref_w_norm * pref_eval["pct"]
            + bonus_w_norm * bonus_eval["pct"]
        )

        all_matched = sorted(list(set(req_eval["matched"] + pref_eval["matched"] + bonus_eval["matched"])))
        all_missing = sorted(list(set(req_eval["missing"] + pref_eval["missing"] + bonus_eval["missing"])))
        all_jd_skills = sorted(list(set(req_parsed + pref_parsed + bonus_parsed)))
        skill_percentage = combined_raw

    else:
        # Uncategorized / Legacy fallback: 70pct skill overlap + 30pct TF-IDF
        if jd_skills is None:
            jd_skills = extract_skills(jd_text)
        jd_lower_map = {s.lower(): s for s in jd_skills}
        matched_keys = set(jd_lower_map.keys()).intersection(set(resume_lower_map.keys()))
        missing_keys = set(jd_lower_map.keys()) - set(resume_lower_map.keys())
        all_matched = sorted([jd_lower_map[k] for k in matched_keys])
        all_missing = sorted([jd_lower_map[k] for k in missing_keys])
        all_jd_skills = sorted(list(jd_lower_map.values()))

        if jd_lower_map:
            skill_pct = (len(matched_keys) / len(jd_lower_map)) * 100.0
        else:
            skill_pct = similarity_percentage

        combined_raw = (0.7 * skill_pct) + (0.3 * similarity_percentage)
        skill_percentage = skill_pct

    final_score = round(max(0.0, min(100.0, combined_raw)), 1)

    return {
        "match_score": final_score,
        "similarity_score": round(similarity_percentage, 1),
        "skill_score": round(skill_percentage, 1),
        "critical_coverage": round(critical_coverage, 1),
        "has_categorized_skills": has_categorized,
        "required": req_eval,
        "preferred": pref_eval,
        "bonus": bonus_eval,
        "matched_skills": all_matched,
        "missing_skills": all_missing,
        "jd_skills": all_jd_skills
    }
