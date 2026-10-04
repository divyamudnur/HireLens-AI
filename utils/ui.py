"""Presentation-only helpers shared by HireLens Streamlit screens."""
from html import escape
import streamlit as st


def apply_hirelens_theme() -> None:
    """Install the app's modern, vibrant, and responsive visual design system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap');
        
        :root {
            --brand-primary: #4F46E5;
            --brand-secondary: #7C3AED;
            --brand-accent: #EC4899;
            --brand-cyan: #06B6D4;
            --ink-dark: #0F172A;
            --ink-muted: #64748B;
            --border-soft: #E2E8F0;
        }

        html, body, [class*="css"], .stMarkdown, p, span, label, input, button, select, textarea {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            letter-spacing: -0.01em;
        }

        /* Ambient vibrant background */
        .stApp {
            background: 
                radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.14) 0%, transparent 40%),
                radial-gradient(circle at 90% 10%, rgba(236, 72, 153, 0.12) 0%, transparent 40%),
                radial-gradient(circle at 50% 90%, rgba(6, 182, 212, 0.10) 0%, transparent 45%),
                #F8FAFC !important;
            color: var(--ink-dark);
        }

        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.8) !important;
            backdrop-filter: blur(8px);
        }

        [data-testid="stAppViewContainer"] .main .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 3.5rem;
        }

        h1, h2, h3, h4 {
            font-family: 'Manrope', sans-serif !important;
            color: var(--ink-dark);
            letter-spacing: -0.03em;
        }

        /* -------------------------------------------------------------
           VIBRANT FORM & CARD STYLING
        ------------------------------------------------------------- */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            border-radius: 22px !important;
            border: 1.5px solid #E0E7FF !important;
            box-shadow: 
                0 20px 40px -12px rgba(99, 102, 241, 0.16),
                0 1px 3px rgba(0, 0, 0, 0.04) !important;
            padding: 1.8rem 1.8rem 1.6rem 1.8rem !important;
            position: relative;
        }

        /* Form labels */
        [data-testid="stForm"] label,
        [data-testid="stWidgetLabel"] p {
            font-size: 0.86rem !important;
            font-weight: 700 !important;
            color: #334155 !important;
        }

        /* Form input fields */
        [data-baseweb="input"] {
            border-radius: 12px !important;
            border: 1.5px solid #CBD5E1 !important;
            background: #F8FAFC !important;
            transition: all 0.2s ease !important;
        }

        [data-baseweb="input"]:focus-within {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 3.5px rgba(99, 102, 241, 0.18) !important;
            background: #FFFFFF !important;
        }

        /* -------------------------------------------------------------
           VIBRANT PRIMARY ACTION BUTTONS
        ------------------------------------------------------------- */
        [data-testid="stFormSubmitButton"] button, 
        .stFormSubmitButton > button,
        [data-testid="stBaseButton-primary"],
        .stButton > button {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.65rem 1.4rem !important;
            min-height: 2.9rem !important;
            box-shadow: 0 6px 20px -2px rgba(99, 102, 241, 0.45) !important;
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
            width: 100% !important;
        }

        [data-testid="stFormSubmitButton"] button:hover, 
        .stFormSubmitButton > button:hover,
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 28px -3px rgba(99, 102, 241, 0.6) !important;
            filter: brightness(1.08) !important;
        }

        [data-testid="stFormSubmitButton"] button:active,
        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        [data-testid="stFormSubmitButton"] button p,
        .stButton > button p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }

        /* -------------------------------------------------------------
           COLORFUL TABS (Pills with Smooth Highlight)
        ------------------------------------------------------------- */
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 6px;
            background: #EEF2FF;
            padding: 5px;
            border-radius: 14px;
            border: 1px solid #E0E7FF;
            margin-bottom: 1.1rem;
            width: 100%;
        }

        [data-testid="stTabs"] button[role="tab"] {
            height: 40px;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            color: #64748B !important;
            background: transparent !important;
            border: none !important;
            flex: 1;
            padding: 0 12px !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stTabs"] button[role="tab"]:hover {
            color: #4F46E5 !important;
            background: rgba(255, 255, 255, 0.8) !important;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
            background: #FFFFFF !important;
            color: #4F46E5 !important;
            box-shadow: 0 2px 10px -1px rgba(99, 102, 241, 0.25) !important;
        }

        [data-testid="stTabs"] button[aria-selected="true"] p {
            color: #4F46E5 !important;
            font-weight: 800 !important;
        }

        /* -------------------------------------------------------------
           SIDEBAR STYLING
        ------------------------------------------------------------- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E1B4B 0%, #2E2A72 60%, #1E293B 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] button {
            background: rgba(255, 255, 255, 0.1) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background: rgba(239, 68, 68, 0.25) !important;
            border-color: #EF4444 !important;
            color: #FCA5A5 !important;
        }

        /* -------------------------------------------------------------
           METRIC CARDS & EXPANDERS
        ------------------------------------------------------------- */
        [data-testid="stMetric"] {
            border: 1.5px solid #E2E8F0;
            background: #FFFFFF;
            border-radius: 16px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.04);
            transition: transform 0.2s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -3px rgba(15, 23, 42, 0.08);
            border-color: #CBD5E1;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            color: #64748B !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stMetricValue"] {
            color: #4F46E5 !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 800 !important;
            font-size: 1.85rem !important;
        }

        [data-testid="stExpander"] {
            border: 1.5px solid #E2E8F0 !important;
            border-radius: 16px !important;
            background: #FFFFFF !important;
            box-shadow: 0 2px 8px -1px rgba(15, 23, 42, 0.03);
            margin-bottom: 0.9rem !important;
            overflow: hidden;
        }

        [data-testid="stExpander"] summary {
            font-weight: 700 !important;
            color: #1E293B !important;
            padding: 0.9rem 1.2rem !important;
        }

        [data-testid="stExpander"] summary:hover {
            background: #F8FAFC !important;
            color: #4F46E5 !important;
        }

        /* -------------------------------------------------------------
           COLORFUL SKILL CHIPS & BADGES
        ------------------------------------------------------------- */
        .hl-chip {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            margin: 3px 4px 3px 0;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            transition: transform 0.15s ease;
        }

        .hl-chip:hover {
            transform: scale(1.05);
        }

        .hl-chip.required {
            background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
            color: #4338CA;
            border: 1px solid #C7D2FE;
        }

        .hl-chip.preferred {
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
            color: #065F46;
            border: 1px solid #A7F3D0;
        }

        .hl-chip.bonus {
            background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
            color: #92400E;
            border: 1px solid #FDE68A;
        }

        /* Progress bar */
        [data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%) !important;
            border-radius: 99px !important;
        }

        [data-testid="stAlert"] {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def skill_chips(value: str, category: str) -> None:
    """Render public skill labels as escaped decorative chips."""
    skills = [part.strip() for part in (value or "").split(",") if part.strip()]
    if skills:
        chips = "".join(
            f'<span class="hl-chip {escape(category)}">{escape(skill)}</span>'
            for skill in skills
        )
        st.markdown(chips, unsafe_allow_html=True)


def score_visual(score: float, label: str = "AI match") -> None:
    """Show the existing score with a visual emphasis; the value is not recalculated."""
    try:
        value = max(0, min(100, float(score)))
    except (TypeError, ValueError):
        value = 0
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1.2rem;padding:1.1rem 1.4rem;'
        f'border:1.5px solid #E0E7FF;border-radius:18px;background:linear-gradient(135deg,#F5F3FF 0%,#FFFFFF 70%);'
        f'margin:0.5rem 0 1rem;box-shadow:0 4px 14px -2px rgba(99,102,241,0.08);">'
        f'<div style="color:#4F46E5;font:800 2.4rem \'Manrope\',sans-serif;line-height:1;">{value:g}%</div>'
        f'<div><strong style="color:#1E1B4B;font-size:1.05rem;">{escape(label)}</strong>'
        f'<div style="color:#64748B;font-size:0.86rem;margin-top:2px;">Deterministic requirement-aware AI score</div></div></div>',
        unsafe_allow_html=True,
    )
    st.progress(value / 100)
