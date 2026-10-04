import streamlit as st
from database.database import initialize_database
from auth.auth import register_user, login_user
from auth.roles import (
    init_session_state,
    login_session,
    logout_session,
    is_authenticated,
    get_current_user,
    get_user_role
)
from candidate.candidate_dashboard import render_candidate_dashboard
from employer.employer_dashboard import render_employer_dashboard
from utils.ui import apply_hirelens_theme
from html import escape

# Ensure database is initialized automatically
initialize_database()

# Page configuration
st.set_page_config(
    page_title="HireLens AI - AI Recruitment Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_hirelens_theme()

# Initialize Session State
init_session_state()

def render_login_page():
    # Spacing for vertical centering
    st.write("")
    st.write("")

    _, auth_col, _ = st.columns([1, 1.15, 1])
    with auth_col:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1.2rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 62px; height: 62px; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%); border-radius: 20px; font-size: 2rem; box-shadow: 0 10px 25px -4px rgba(99, 102, 241, 0.45); margin-bottom: 0.8rem;">🎯</div>
                <div style="font-family: 'Manrope', sans-serif; font-size: 1.9rem; font-weight: 800; background: linear-gradient(135deg, #1E1B4B 0%, #4338CA 50%, #EC4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;">HireLens AI</div>
                <div style="font-size: 0.9rem; color: #64748B; font-weight: 600; margin-top: 4px;">Intelligent AI Recruitment Platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("🚀 Sign In to Workspace", use_container_width=True)

                if submit:
                    user, msg = login_user(email, password)
                    if user:
                        login_session(user)
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab2:
            with st.form("register_form", clear_on_submit=True):
                name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
                email = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password (min 6 chars)", type="password", placeholder="Create a password")
                role = st.selectbox("I am joining as", options=["Candidate", "Employer"])
                submit = st.form_submit_button("🌟 Create Account", use_container_width=True)

                if submit:
                    success, msg = register_user(name, email, password, role.lower())
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown(
            '<div style="text-align: center; margin-top: 1rem;">'
            '<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 0.76rem; font-weight: 700; color: #059669; background: #ECFDF5; padding: 6px 14px; border-radius: 20px; border: 1px solid #A7F3D0; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">'
            '🔒 100% Local & Encrypted · Zero Cloud Leakage'
            '</span></div>',
            unsafe_allow_html=True,
        )

def main():
    if not is_authenticated():
        render_login_page()
    else:
        user = get_current_user()
        role = get_user_role()

        # Sidebar user section
        with st.sidebar:
            st.markdown('<div class="hl-brand">◉ &nbsp; HireLens AI</div>', unsafe_allow_html=True)
            st.caption("AI talent matching")
            st.markdown(f"### {escape(str(user['name']))}")
            st.caption(escape(str(user['email'])))
            st.markdown(f"**{role.title()} workspace**")
            st.markdown("---")
            if st.button("🚪 Log Out", use_container_width=True):
                logout_session()
                st.rerun()

        # Role-based dashboard rendering
        if role == 'candidate':
            render_candidate_dashboard()
        elif role == 'employer':
            render_employer_dashboard()
        else:
            st.error("Unknown user role.")

if __name__ == "__main__":
    main()
