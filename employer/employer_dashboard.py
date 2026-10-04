import streamlit as st
from auth.roles import get_current_user
from jobs.job_manager import (
    create_job,
    get_employer_jobs,
    get_job_applicants,
    update_application_status,
    get_application_match_details
)

# Colour map for recommendation badges
_REC_COLOURS = {
    "STRONG MATCH":  "#16a34a",   # green
    "GOOD MATCH":    "#2563eb",   # blue
    "PARTIAL MATCH": "#d97706",   # amber
    "WEAK MATCH":    "#dc2626",   # red
}

_SEV_COLOURS = {
    "HIGH":   "#dc2626",
    "MEDIUM": "#d97706",
    "LOW":    "#6b7280",
}


def _badge(label: str, colour: str) -> str:
    return (
        f'<span style="background:{colour};color:#fff;padding:2px 10px;'
        f'border-radius:12px;font-size:0.82rem;font-weight:700;">{label}</span>'
    )


def _render_why_this_candidate(match_info: dict, candidate_name: str) -> None:
    """Renders the recruiter-only 'Why This Candidate?' section."""
    rec = match_info.get("recommendation", {})
    flags = match_info.get("verification_flags", [])
    vsummary = match_info.get("verification_summary", {})
    quality = match_info.get("resume_quality", {})

    if not rec:
        return

    recommendation = rec.get("recommendation", "N/A")
    rec_colour = _REC_COLOURS.get(recommendation, "#6b7280")

    st.markdown("#### 🧠 Why This Candidate?")

    col_a, col_b, col_c = st.columns([2, 2, 2])
    with col_a:
        st.markdown(
            f"**Recommendation:** " + _badge(recommendation, rec_colour),
            unsafe_allow_html=True
        )
    with col_b:
        st.metric("Overall Match", f"{rec.get('overall_score', 0.0)}%")
    with col_c:
        st.metric("Critical Skill Coverage", f"{rec.get('critical_coverage', 0.0)}%")

    # Resume quality indicator
    if quality:
        qlevel = quality.get("level", "UNKNOWN")
        qicon  = quality.get("icon", "")
        st.markdown(
            f"**Resume Quality:** {qicon} `{qlevel}` "
            f"({quality.get('word_count', 0)} words, "
            f"{quality.get('skill_count', 0)} skills detected)"
        )
        if quality.get("warning"):
            st.warning(quality["warning"])

    # Top Strengths
    strengths = rec.get("top_strengths", [])
    if strengths:
        with st.expander("✅ Top Strengths", expanded=True):
            for s in strengths:
                st.markdown(f"- {s}")

    # Critical Gaps
    crit_gaps = rec.get("critical_gaps", [])
    pref_gaps = rec.get("preferred_gaps", [])
    if crit_gaps or pref_gaps:
        with st.expander("⚠️ Skill Gaps"):
            if crit_gaps:
                st.markdown("**Missing Required Skills:**")
                for g in crit_gaps:
                    st.markdown(f"  - `{g}`")
            if pref_gaps:
                st.markdown("**Missing Preferred Skills:**")
                for g in pref_gaps:
                    st.markdown(f"  - `{g}`")

    # Verification Flags (recruiter-only)
    if flags:
        with st.expander(
            f"🔍 Verification Flags ({vsummary.get('total_flags', 0)}) — Recruiter Review",
            expanded=False
        ):
            st.info(
                "These flags are recruiter review signals only. "
                "They do NOT indicate dishonesty or fraud. "
                "All candidates deserve fair consideration."
            )
            for f in flags:
                sev = f.get("severity", "LOW")
                colour = _SEV_COLOURS.get(sev, "#6b7280")
                st.markdown(
                    _badge(sev, colour) + f"  **{f.get('type', '')}**",
                    unsafe_allow_html=True
                )
                st.markdown(f"  {f.get('explanation', '')}")
                if f.get("evidence"):
                    st.caption(f"Evidence: {f['evidence']}")
                st.markdown("---")
    elif vsummary.get("total_flags", 0) == 0:
        st.success("No verification flags — resume appears internally consistent.")

    # Recruiter notes
    notes = rec.get("recruiter_notes", [])
    if notes:
        with st.expander("📋 Recruiter Notes"):
            for note in notes:
                st.markdown(f"- {note}")


def render_employer_dashboard():
    """Renders the Employer Dashboard with Requirement-Aware Job Creation & Applicant Ranking."""
    user = get_current_user()
    if not user:
        st.error("User session expired. Please log in again.")
        return

    st.title("💼 Employer Dashboard")
    st.subheader(f"Welcome back, 👋 {user['name']}!")

    tab1, tab2 = st.tabs(["➕ Post a New Job", "📋 My Posted Jobs & Ranked Applicants"])

    # ── TAB 1: POST A NEW JOB ──────────────────────────────────────────────
    with tab1:
        st.subheader("Create a New Job Listing")
        with st.form("create_job_form", clear_on_submit=True):
            title    = st.text_input("Job Title *", placeholder="e.g. Senior Python Developer")
            company  = st.text_input("Company Name *", placeholder="e.g. Acme Tech Solutions")
            location = st.text_input("Location", placeholder="e.g. New York, NY or Remote")
            description = st.text_area(
                "Job Description & Requirements *", height=120,
                placeholder="Describe position responsibilities, skills, and qualifications..."
            )

            st.markdown("#### 🎯 Categorized Skill Priorities (Optional)")
            st.caption(
                "Scoring formula: **40% TF-IDF** + **40% Required** + **15% Preferred** + **5% Bonus**. "
                "All three categories are optional. Old jobs without these fields continue to work."
            )
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                req_skills = st.text_input(
                    "Required Skills (comma-separated)",
                    placeholder="e.g. Python, Docker, SQL",
                    help="Highest priority — 40% of final score."
                )
            with col_s2:
                pref_skills = st.text_input(
                    "Preferred Skills (comma-separated)",
                    placeholder="e.g. React, AWS",
                    help="Medium priority — 15% of final score."
                )
            with col_s3:
                bon_skills = st.text_input(
                    "Bonus Skills (comma-separated)",
                    placeholder="e.g. Kubernetes, GraphQL",
                    help="Bonus priority — 5% of final score."
                )

            submit = st.form_submit_button("Post Job", use_container_width=True)

            if submit:
                success, msg, job_id = create_job(
                    employer_id=user["id"],
                    title=title,
                    company=company,
                    description=description,
                    location=location,
                    required_skills=req_skills,
                    preferred_skills=pref_skills,
                    bonus_skills=bon_skills
                )
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ── TAB 2: MANAGE JOBS & RANKED APPLICANTS ─────────────────────────────
    with tab2:
        st.subheader("Your Job Listings & Ranked Applicants")
        my_jobs = get_employer_jobs(user["id"])

        if not my_jobs:
            st.info("You haven't posted any jobs yet. Use the 'Post a New Job' tab to get started!")
        else:
            for job in my_jobs:
                with st.expander(
                    f"💼 {job['title']} — {job['company']} ({job.get('location') or 'Remote'})",
                    expanded=False
                ):
                    st.write(f"**Posted Date:** {job['created_at']}")
                    st.markdown("**Job Description:**")
                    st.write(job["description"])

                    if job.get("required_skills") or job.get("preferred_skills") or job.get("bonus_skills"):
                        st.markdown("**Skill Priorities:**")
                        if job.get("required_skills"):
                            st.write(f"- **Required:** `{job['required_skills']}`")
                        if job.get("preferred_skills"):
                            st.write(f"- **Preferred:** `{job['preferred_skills']}`")
                        if job.get("bonus_skills"):
                            st.write(f"- **Bonus:** `{job['bonus_skills']}`")

                    st.markdown("---")
                    st.markdown("#### 🔍 Search & Filter Applicants")
                    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])

                    with f_col1:
                        search_query = st.text_input("Search Name / Email", key=f"search_{job['id']}")
                    with f_col2:
                        min_score = st.slider("Min Match Score %", 0, 100, 0, key=f"min_score_{job['id']}")
                    with f_col3:
                        status_filter = st.selectbox(
                            "Filter by Status",
                            options=["All", "Applied", "Shortlisted", "Rejected"],
                            key=f"status_filter_{job['id']}"
                        )

                    f_col4, f_col5 = st.columns([3, 3])
                    with f_col4:
                        skill_keyword = st.text_input(
                            "Filter by Matched Skill", key=f"skill_filter_{job['id']}"
                        )
                    with f_col5:
                        sort_choice = st.selectbox(
                            "Sort Applicants By",
                            options=[
                                "Match Score (High to Low)",
                                "Match Score (Low to High)",
                                "Application Date (Newest)",
                                "Application Date (Oldest)"
                            ],
                            key=f"sort_select_{job['id']}"
                        )

                    sort_mapping = {
                        "Match Score (High to Low)": "match_score_desc",
                        "Match Score (Low to High)": "match_score_asc",
                        "Application Date (Newest)": "date_desc",
                        "Application Date (Oldest)": "date_asc"
                    }

                    applicants = get_job_applicants(
                        job["id"], user["id"],
                        sort_by=sort_mapping.get(sort_choice, "match_score_desc")
                    )

                    filtered_applicants = []
                    for app in applicants:
                        if search_query:
                            q = search_query.lower().strip()
                            if (q not in app["candidate_name"].lower()
                                    and q not in app["candidate_email"].lower()):
                                continue

                        if app["match_score"] < min_score:
                            continue

                        if status_filter != "All" and app["status"] != status_filter:
                            continue

                        if skill_keyword:
                            sk = skill_keyword.lower().strip()
                            mi = get_application_match_details(
                                app["application_id"],
                                requesting_user_id=user["id"],
                                is_employer_check=True
                            )
                            matched_skills = [s.lower() for s in mi.get("matched_skills", [])]
                            if sk not in matched_skills:
                                continue

                        filtered_applicants.append(app)

                    st.markdown("---")
                    st.write(f"### 🏆 Ranked Applicants ({len(filtered_applicants)} of {len(applicants)})")

                    if not filtered_applicants:
                        st.info("No candidates match your current search / filter criteria.")
                    else:
                        for app in filtered_applicants:
                            match_info = get_application_match_details(
                                app["application_id"],
                                requesting_user_id=user["id"],
                                is_employer_check=True
                            )

                            with st.container():
                                col_rank, col1, col2, col3 = st.columns([1, 4, 2, 3])

                                with col_rank:
                                    rv = app["rank"]
                                    badge = (
                                        "🥇 #1" if rv == 1 else
                                        "🥈 #2" if rv == 2 else
                                        "🥉 #3" if rv == 3 else
                                        f"#{rv}"
                                    )
                                    st.markdown(f"### {badge}")

                                with col1:
                                    st.write(f"**{app['candidate_name']}** ({app['candidate_email']})")
                                    st.caption(f"Applied on: {app['applied_at']}")
                                    st.caption(f"Resume: `{app['resume_path']}`")

                                    # Resume quality inline badge
                                    rq = match_info.get("resume_quality", {})
                                    if rq:
                                        st.caption(
                                            f"Resume Quality: {rq.get('icon','')} {rq.get('level','')}"
                                        )

                                with col2:
                                    score_val = app["match_score"]
                                    st.metric(label="Match Score", value=f"{score_val}%")
                                    st.progress(float(score_val) / 100.0)

                                    # Recommendation badge
                                    rec = match_info.get("recommendation", {})
                                    if rec and rec.get("recommendation"):
                                        rname = rec["recommendation"]
                                        rcol  = _REC_COLOURS.get(rname, "#6b7280")
                                        st.markdown(_badge(rname, rcol), unsafe_allow_html=True)

                                with col3:
                                    st.write("**Application Status:**")
                                    current_status = app["status"]
                                    new_status = st.selectbox(
                                        "Update Status",
                                        options=["Applied", "Shortlisted", "Rejected"],
                                        index=["Applied", "Shortlisted", "Rejected"].index(current_status),
                                        key=f"status_select_{app['application_id']}"
                                    )
                                    if st.button("Save Status", key=f"save_status_btn_{app['application_id']}"):
                                        success, msg = update_application_status(
                                            app["application_id"], new_status, user["id"]
                                        )
                                        if success:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)

                            # ── Why This Candidate? ───────────────────────────────────
                            if match_info and not match_info.get("error"):
                                with st.expander(
                                    f"🧠 Why This Candidate? — Rank #{app['rank']} | {app['candidate_name']}",
                                    expanded=False
                                ):
                                    _render_why_this_candidate(match_info, app["candidate_name"])

                                # Detailed AI match breakdown
                                if match_info.get("explanation"):
                                    with st.expander(
                                        f"📊 Detailed AI Match Analysis — Rank #{app['rank']} | {app['candidate_name']}",
                                        expanded=False
                                    ):
                                        st.markdown(match_info["explanation"])

                            st.markdown("---")
