import streamlit as st

# Role Constants
ROLE_CANDIDATE = "candidate"
ROLE_EMPLOYER = "employer"

def init_session_state():
    """Initializes authentication session variables in Streamlit session_state."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

def login_session(user_data: dict):
    """Sets session state for logged-in user."""
    st.session_state.user = user_data
    st.session_state.authenticated = True

def logout_session():
    """Clears user session state on logout."""
    st.session_state.user = None
    st.session_state.authenticated = False

def is_authenticated() -> bool:
    """Returns True if a user is currently logged in."""
    return st.session_state.get("authenticated", False) and st.session_state.get("user") is not None

def get_current_user() -> dict | None:
    """Returns current logged-in user info dictionary or None."""
    return st.session_state.get("user")

def get_user_role() -> str | None:
    """Returns current user's role ('candidate' or 'employer') or None."""
    user = get_current_user()
    return user.get("role") if user else None

def is_candidate(user: dict = None) -> bool:
    """Checks if the given user (or currently logged-in user) is a candidate."""
    if user is None:
        user = get_current_user()
    return user is not None and user.get("role") == ROLE_CANDIDATE

def is_employer(user: dict = None) -> bool:
    """Checks if the given user (or currently logged-in user) is an employer."""
    if user is None:
        user = get_current_user()
    return user is not None and user.get("role") == ROLE_EMPLOYER

def check_role(required_role: str, user: dict = None) -> bool:
    """Verifies if user has the specified required_role."""
    if user is None:
        user = get_current_user()
    return user is not None and user.get("role") == required_role.lower()
