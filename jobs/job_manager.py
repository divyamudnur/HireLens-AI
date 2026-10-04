import sqlite3
import os
from database.database import get_connection
from ai.resume_parser import extract_text_from_pdf
from ai.scorer import calculate_match_score
from ai.explainer import generate_match_explanation, generate_candidate_feedback
from ai.quality import assess_resume_quality
from ai.verifier import verify_resume_claims, get_verification_summary
from ai.recommender import get_recommendation
from ai.text_processor import extract_skills


def create_job(
    employer_id: int,
    title: str,
    company: str,
    description: str,
    location: str,
    required_skills: str = "",
    preferred_skills: str = "",
    bonus_skills: str = ""
) -> tuple[bool, str, int | None]:
    """Creates a new job posting for an employer with optional categorized skills."""
    title       = title.strip()       if title       else ""
    company     = company.strip()     if company     else ""
    description = description.strip() if description else ""
    location    = location.strip()    if location    else ""
    req_skills  = required_skills.strip()  if required_skills  else ""
    pref_skills = preferred_skills.strip() if preferred_skills else ""
    bon_skills  = bonus_skills.strip()     if bonus_skills     else ""

    if not title or not company or not description:
        return False, "Job title, company, and description are required fields.", None

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs
              (employer_id, title, company, description, location,
               required_skills, preferred_skills, bonus_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (employer_id, title, company, description, location,
             req_skills, pref_skills, bon_skills)
        )
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, "Job posted successfully!", job_id
    except Exception as e:
        return False, f"Failed to post job: {str(e)}", None


def get_all_jobs() -> list[dict]:
    """Returns a list of all posted jobs."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.id, j.employer_id, j.title, j.company, j.description, j.location,
                   COALESCE(j.required_skills,  '') AS required_skills,
                   COALESCE(j.preferred_skills, '') AS preferred_skills,
                   COALESCE(j.bonus_skills,     '') AS bonus_skills,
                   j.created_at,
                   u.name  AS employer_name,
                   u.email AS employer_email
            FROM jobs j
            JOIN users u ON j.employer_id = u.id
            ORDER BY j.created_at DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def get_job_by_id(job_id: int) -> dict | None:
    """Returns a single job by its ID."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT j.id, j.employer_id, j.title, j.company, j.description, j.location,
                   COALESCE(j.required_skills,  '') AS required_skills,
                   COALESCE(j.preferred_skills, '') AS preferred_skills,
                   COALESCE(j.bonus_skills,     '') AS bonus_skills,
                   j.created_at,
                   u.name AS employer_name
            FROM jobs j
            JOIN users u ON j.employer_id = u.id
            WHERE j.id = ?
            """,
            (job_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        return None


def get_employer_jobs(employer_id: int) -> list[dict]:
    """Returns all jobs posted by a specific employer."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, employer_id, title, company, description, location,
                   COALESCE(required_skills,  '') AS required_skills,
                   COALESCE(preferred_skills, '') AS preferred_skills,
                   COALESCE(bonus_skills,     '') AS bonus_skills,
                   created_at
            FROM jobs
            WHERE employer_id = ?
            ORDER BY created_at DESC
            """,
            (employer_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def has_candidate_applied(candidate_id: int, job_id: int) -> bool:
    """Checks if a candidate has already applied to a specific job."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM applications WHERE candidate_id = ? AND job_id = ?",
            (candidate_id, job_id)
        )
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False


def create_application(candidate_id: int, job_id: int, resume_path: str) -> tuple[bool, str]:
    """
    Submits a job application for a candidate.
    Calculates Requirement-Aware TF-IDF + Skill Priority score and persists it.
    Prevents duplicate applications.
    """
    if has_candidate_applied(candidate_id, job_id):
        return False, "You have already applied for this job."

    if not resume_path or not os.path.exists(resume_path):
        return False, "A valid resume file is required."

    try:
        job = get_job_by_id(job_id)
        if not job:
            return False, "Target job listing not found."

        parse_ok, resume_text, _ = extract_text_from_pdf(resume_path)

        if parse_ok and resume_text:
            match_res = calculate_match_score(
                resume_text=resume_text,
                jd_text=job["description"],
                required_skills=job.get("required_skills", ""),
                preferred_skills=job.get("preferred_skills", ""),
                bonus_skills=job.get("bonus_skills", "")
            )
            calculated_score = match_res["match_score"]
        else:
            calculated_score = 0.0

        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO applications (candidate_id, job_id, resume_path, match_score, status)
            VALUES (?, ?, ?, ?, 'Applied')
            """,
            (candidate_id, job_id, resume_path, calculated_score)
        )
        conn.commit()
        conn.close()
        return True, "Application submitted successfully!"
    except Exception as e:
        return False, f"Failed to submit application: {str(e)}"


def get_candidate_applications(candidate_id: int) -> list[dict]:
    """Returns all applications submitted by a candidate with job details."""
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id AS application_id, a.job_id, a.resume_path,
                   COALESCE(a.match_score, 0.0) AS match_score,
                   a.status, a.applied_at,
                   j.title, j.company, j.location, j.description,
                   COALESCE(j.required_skills,  '') AS required_skills,
                   COALESCE(j.preferred_skills, '') AS preferred_skills,
                   COALESCE(j.bonus_skills,     '') AS bonus_skills
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.candidate_id = ?
            ORDER BY a.applied_at DESC
            """,
            (candidate_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def get_job_applicants(
    job_id: int,
    employer_id: int,
    sort_by: str = "match_score_desc"
) -> list[dict]:
    """
    Returns all applicants for a specific job ranked by match_score.
    Enforces employer ownership.
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT employer_id FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if not job or job["employer_id"] != employer_id:
            conn.close()
            return []

        order_sql = "COALESCE(a.match_score, 0.0) DESC, a.applied_at DESC"
        if sort_by == "match_score_asc":
            order_sql = "COALESCE(a.match_score, 0.0) ASC, a.applied_at DESC"
        elif sort_by == "date_desc":
            order_sql = "a.applied_at DESC"
        elif sort_by == "date_asc":
            order_sql = "a.applied_at ASC"

        cursor.execute(
            f"""
            SELECT a.id AS application_id, a.candidate_id, a.job_id, a.resume_path,
                   COALESCE(a.match_score, 0.0) AS match_score,
                   a.status, a.applied_at,
                   u.name  AS candidate_name,
                   u.email AS candidate_email,
                   j.description AS job_description,
                   COALESCE(j.required_skills,  '') AS required_skills,
                   COALESCE(j.preferred_skills, '') AS preferred_skills,
                   COALESCE(j.bonus_skills,     '') AS bonus_skills
            FROM applications a
            JOIN users u ON a.candidate_id = u.id
            JOIN jobs  j ON a.job_id       = j.id
            WHERE a.job_id = ?
            ORDER BY {order_sql}
            """,
            (job_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        applicants = [dict(row) for row in rows]
        for idx, app in enumerate(applicants, start=1):
            app["rank"] = idx
        return applicants
    except Exception:
        return []


def get_application_match_details(
    application_id: int,
    requesting_user_id: int = None,
    is_employer_check: bool = False
) -> dict:
    """
    Calculates full requirement-aware match details, resume quality,
    claim verification flags, and recruiter recommendation.
    Enforces ownership security.

    Candidates receive: match breakdown + candidate feedback (no flags).
    Employers receive:  match breakdown + verification flags + recommendation.
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.candidate_id, a.resume_path,
                   COALESCE(a.match_score, 0.0) AS match_score,
                   j.employer_id,
                   j.description AS job_description,
                   COALESCE(j.required_skills,  '') AS required_skills,
                   COALESCE(j.preferred_skills, '') AS preferred_skills,
                   COALESCE(j.bonus_skills,     '') AS bonus_skills
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
            """,
            (application_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        # Security check
        if requesting_user_id is not None:
            if is_employer_check and row["employer_id"] != requesting_user_id:
                return {"error": "Unauthorized access to applicant match details."}
            elif not is_employer_check and row["candidate_id"] != requesting_user_id:
                return {"error": "Unauthorized access to application match details."}

        resume_path = row["resume_path"]
        jd_text     = row["job_description"]

        if not resume_path or not os.path.exists(resume_path):
            return {
                "match_score": row["match_score"],
                "similarity_score": 0.0,
                "skill_score": 0.0,
                "critical_coverage": 0.0,
                "has_categorized_skills": False,
                "explanation": "Resume file missing or unreadable.",
                "candidate_feedback": "Resume file missing or unreadable.",
                "resume_quality": {
                    "level": "POOR", "warning": "Resume file not found.",
                    "icon": "🔴", "word_count": 0, "char_count": 0,
                    "skill_count": 0, "parse_success": False
                }
            }

        parse_ok, resume_text, parse_msg = extract_text_from_pdf(resume_path)

        # Resume quality assessment (always computed)
        detected_skills_for_quality = extract_skills(resume_text) if parse_ok and resume_text else []
        quality = assess_resume_quality(parse_ok, resume_text or "", detected_skills_for_quality)

        if not parse_ok:
            return {
                "match_score": row["match_score"],
                "similarity_score": 0.0,
                "skill_score": 0.0,
                "critical_coverage": 0.0,
                "has_categorized_skills": False,
                "explanation": "Could not extract text from uploaded PDF resume.",
                "candidate_feedback": "Could not extract text from your PDF resume.",
                "resume_quality": quality
            }

        match_res = calculate_match_score(
            resume_text=resume_text,
            jd_text=jd_text,
            required_skills=row["required_skills"],
            preferred_skills=row["preferred_skills"],
            bonus_skills=row["bonus_skills"]
        )

        # Standard explanation (recruiter-facing)
        explanation = generate_match_explanation(match_res)
        match_res["explanation"] = explanation

        # Candidate-facing feedback (no recruiter-private data)
        match_res["candidate_feedback"] = generate_candidate_feedback(match_res)

        # Resume quality
        match_res["resume_quality"] = quality

        # Claim verification + recommendation (employer-only enrichment)
        if is_employer_check:
            flags = verify_resume_claims(
                resume_text=resume_text,
                resume_skills=match_res.get("matched_skills", [])
            )
            vsummary = get_verification_summary(flags)
            recommendation = get_recommendation(match_res, flags)

            match_res["verification_flags"]   = flags
            match_res["verification_summary"] = vsummary
            match_res["recommendation"]       = recommendation
        else:
            # Candidates never see verification flags or recruiter recommendations
            match_res["verification_flags"]   = []
            match_res["verification_summary"] = {}
            match_res["recommendation"]       = {}

        return match_res

    except Exception:
        return {}


def update_application_status(
    application_id: int,
    new_status: str,
    employer_id: int
) -> tuple[bool, str]:
    """Updates application status. Enforces employer ownership."""
    valid_statuses = ["Applied", "Shortlisted", "Rejected"]
    if new_status not in valid_statuses:
        return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT a.id, j.employer_id
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
            """,
            (application_id,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Application not found."

        if row["employer_id"] != employer_id:
            conn.close()
            return False, "Unauthorized: You do not own the job posting for this application."

        cursor.execute(
            "UPDATE applications SET status = ? WHERE id = ?",
            (new_status, application_id)
        )
        conn.commit()
        conn.close()
        return True, f"Application status updated to '{new_status}'."
    except Exception as e:
        return False, f"Failed to update status: {str(e)}"
