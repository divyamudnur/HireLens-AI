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

# Ensure database is initialized automatically
initialize_database()

# Page configuration
st.set_page_config(
    page_title="HireLens AI - AI Recruitment Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    .user-badge {
        background-color: #E2E8F0;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
init_session_state()

def render_login_page():
    st.markdown('<div class="main-title">🎯 HireLens AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Role-Based AI Recruitment Platform</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email Address", placeholder="e.g. john@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Log In", use_container_width=True)

            if submit:
                user, msg = login_user(email, password)
                if user:
                    login_session(user)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        st.subheader("Create a new account")
        with st.form("register_form", clear_on_submit=True):
            name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
            email = st.text_input("Email Address", placeholder="e.g. jane@example.com")
            password = st.text_input("Password (min 6 chars)", type="password", placeholder="••••••••")
            role = st.selectbox("I am a:", options=["Candidate", "Employer"])
            submit = st.form_submit_button("Register", use_container_width=True)

            if submit:
                success, msg = register_user(name, email, password, role.lower())
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def main():
    if not is_authenticated():
        render_login_page()
    else:
        user = get_current_user()
        role = get_user_role()

        # Sidebar user section
        with st.sidebar:
            st.title("🎯 HireLens AI")
            st.markdown(f"**User:** {user['name']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Role:** `{role.upper()}`")
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
