import streamlit as st
from auth.roles import get_current_user
from jobs.job_manager import (
    get_all_jobs,
    has_candidate_applied,
    create_application,
    get_candidate_applications,
    get_application_match_details
)
from utils.helpers import save_uploaded_resume
from ai.resume_parser import extract_text_from_pdf
from ai.text_processor import process_resume_text
from ai.quality import assess_resume_quality


def _render_candidate_match_feedback(match_info: dict, app: dict) -> None:
    """
    Renders candidate-facing match feedback.
    NEVER exposes: verification flags, other candidates' scores,
    recruiter recommendations, or private employer data.
    """
    score = app.get("match_score", 0.0)
    quality = match_info.get("resume_quality", {})
    feedback = match_info.get("candidate_feedback", "")

    # Resume quality warning for candidate
    if quality and quality.get("warning"):
        st.warning(quality["warning"])

    # Candidate-friendly feedback
    if feedback:
        st.markdown(feedback)
    elif match_info.get("explanation"):
        st.markdown(match_info["explanation"])


def render_candidate_dashboard():
    """Renders the Candidate Dashboard."""
    user = get_current_user()
    if not user:
        st.error("User session expired. Please log in again.")
        return

    st.title("🎯 Candidate Dashboard")
    st.subheader(f"Welcome back, 👋 {user['name']}!")

    tab1, tab2 = st.tabs(["💼 Browse Available Jobs", "📋 My Applications"])

    # ── TAB 1: BROWSE JOBS ────────────────────────────────────────────────
    with tab1:
        st.subheader("Available Job Openings")
        jobs = get_all_jobs()

        if not jobs:
            st.info("No jobs have been posted yet. Check back soon!")
        else:
            for job in jobs:
                with st.expander(
                    f"📌 {job['title']} — {job['company']} ({job.get('location') or 'Remote'})",
                    expanded=False
                ):
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Location:** {job.get('location') or 'Remote'}")
                    st.write(f"**Posted By:** {job['employer_name']}")
                    st.write(f"**Posted On:** {job['created_at']}")
                    st.markdown("---")
                    st.markdown("**Job Description:**")
                    st.write(job["description"])

                    # Show public skill requirements (no scoring weights exposed)
                    if job.get("required_skills") or job.get("preferred_skills") or job.get("bonus_skills"):
                        st.markdown("**Skills Sought:**")
                        if job.get("required_skills"):
                            st.write(f"- **Required:** {job['required_skills']}")
                        if job.get("preferred_skills"):
                            st.write(f"- **Preferred:** {job['preferred_skills']}")
                        if job.get("bonus_skills"):
                            st.write(f"- **Bonus:** {job['bonus_skills']}")

                    st.markdown("---")

                    already_applied = has_candidate_applied(user["id"], job["id"])

                    if already_applied:
                        st.success("✅ You have already applied for this job.")
                    else:
                        st.subheader("Apply for this Position")
                        uploaded_file = st.file_uploader(
                            f"Upload PDF Resume for '{job['title']}'",
                            type=["pdf"],
                            key=f"resume_upload_{job['id']}"
                        )

                        if st.button(
                            f"Submit Application for {job['title']}",
                            key=f"btn_apply_{job['id']}"
                        ):
                            if not uploaded_file:
                                st.error("Please upload a PDF resume before submitting.")
                            else:
                                rel_path, save_msg = save_uploaded_resume(
                                    uploaded_file, user["id"], job["id"]
                                )
                                if not rel_path:
                                    st.error(save_msg)
                                else:
                                    parse_ok, raw_text, parse_msg = extract_text_from_pdf(rel_path)

                                    # Show quality indicator before submitting
                                    if parse_ok and raw_text:
                                        proc = process_resume_text(raw_text)
                                        quality = assess_resume_quality(
                                            parse_ok, raw_text, proc["detected_skills"]
                                        )
                                        if quality["level"] == "GOOD":
                                            st.success(
                                                f"Resume parsed successfully — "
                                                f"{quality['word_count']} words, "
                                                f"{quality['skill_count']} skills detected."
                                            )
                                        elif quality["level"] == "LIMITED":
                                            st.warning(quality["warning"])
                                        else:
                                            st.error(quality["warning"])

                                    if not parse_ok:
                                        st.error(f"Resume Parsing Error: {parse_msg}")
                                    else:
                                        success, app_msg = create_application(
                                            user["id"], job["id"], rel_path
                                        )
                                        if success:
                                            st.success(app_msg)
                                            st.rerun()
                                        else:
                                            st.error(app_msg)

    # ── TAB 2: MY APPLICATIONS ─────────────────────────────────────────────
    with tab2:
        st.subheader("Your Submitted Applications")
        apps = get_candidate_applications(user["id"])

        if not apps:
            st.info("You haven't applied to any jobs yet.")
        else:
            for app in apps:
                status = app["status"]
                status_display = {
                    "Applied":     "🟦 Applied",
                    "Shortlisted": "🟩 Shortlisted",
                    "Rejected":    "🟥 Rejected"
                }.get(status, status)

                # Fetch match details — candidate perspective (no verification flags)
                match_info = get_application_match_details(
                    app["application_id"],
                    requesting_user_id=user["id"],
                    is_employer_check=False
                )

                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.write(f"### {app['title']}")
                        st.write(
                            f"**Company:** {app['company']} | "
                            f"**Location:** {app.get('location') or 'Remote'}"
                        )
                        st.caption(f"Applied on: {app['applied_at']}")
                    with col2:
                        st.write("**Application Status:**")
                        if status == "Shortlisted":
                            st.success(f"**{status_display}**")
                        elif status == "Rejected":
                            st.error(f"**{status_display}**")
                        else:
                            st.info(f"**{status_display}**")
                    with col3:
                        st.write("**AI Match Score:**")
                        score_val = app["match_score"]
                        st.metric(label="Match Score", value=f"{score_val}%")
                        st.progress(float(score_val) / 100.0)

                # Candidate-facing feedback (privacy-safe)
                if match_info and not match_info.get("error"):
                    with st.expander("🤖 View AI Match Breakdown & Skill Gap Feedback"):
                        _render_candidate_match_feedback(match_info, app)

                st.markdown("---")
