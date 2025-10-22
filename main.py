
import streamlit as st
import base64
import pandas as pd
import altair as alt
from cohere_handler import analyze_code, explain_code
from database import register_user, verify_user, save_review, get_user_reviews
from utils import get_syntax_highlighted_code

# =============================
# 🔧 Initialization
# =============================
def init_app():
    st.set_page_config(page_title="AI Code Reviewer", page_icon="🧠", layout="wide")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None


# =============================
# 📂 Utility Functions
# =============================
def get_download_link(text, filename, filetype="txt"):
    """Generate a download link for feedback"""
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/{filetype};base64,{b64}" download="{filename}">📥 Download Feedback</a>'


# =============================
# 🔐 Authentication Section
# =============================
def auth_section():
    st.markdown("""<style> ... </style>""", unsafe_allow_html=True)  # keep your CSS

    st.markdown("""
    <div class='login-wrapper'>
        <div class='login-container'>
            <h2 style='text-align:left; color:white;'>🔍 AI Code Reviewer</h2>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab1:
        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;'>", unsafe_allow_html=True)
        username = st.text_input("👤 Username", placeholder="Enter username", key="login_username", label_visibility="visible")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="login_password", label_visibility="visible")
        if st.button("Login"):
            try:
                user_id = verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            except Exception as e:
                st.error(f"⚠️ Login error: {e}")
        st.markdown("<p class='forgot-password'>Forgot Password?</p>", unsafe_allow_html=True)

    with tab2:
        new_user = st.text_input("🆕 New Username", width=500)
        new_pass = st.text_input("🔐 New Password", type="password")
        confirm_pass = st.text_input("🔁 Confirm Password", type="password")
        if st.button("Sign Up"):
            if new_pass == confirm_pass:
                try:
                    user_id = register_user(new_user, new_pass)
                    if user_id:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.success("✅ Registration successful! Logging you in...")
                        st.rerun()
                    else:
                        st.error("❌ Registration failed. Try a different username.")
                except Exception as e:
                    st.error(f"⚠️ Registration error: {e}")
            else:
                st.error("❌ Passwords do not match.")

    st.markdown("</div></div>", unsafe_allow_html=True)


# =============================
# 🧠 Main Application
# =============================
def main_app():
    st.title("🧠 AI-Powered Code Reviewer")

    st.subheader("Input Your Code")
    input_method = st.radio("Input method:", ["Text Area", "File Upload"], horizontal=True)

    language = st.selectbox("Programming Language", ["Python", "JavaScript", "Java", "C++", "Go"])
    advanced_mode = st.checkbox("Advanced Analysis")

    code = ""
    if input_method == "Text Area":
        code = st.text_area("Paste code here:", placeholder="// Your code here...", height=300, key="code_area")
    else:
        uploaded_file = st.file_uploader("Upload file", type=["py", "js", "java", "cpp", "go"], key="file_uploader")
        if uploaded_file:
            code = uploaded_file.getvalue().decode("utf-8")

    # 🔍 Analyze Code
    if st.button("Analyze Code", type="primary") and code:
        with st.spinner("Analyzing your code..."):
            try:
                analysis = analyze_code(code=code, language=language.lower(), advanced=advanced_mode)
                st.subheader("Analysis Results")
                st.markdown("### Original Code")
                st.markdown(get_syntax_highlighted_code(code, language), unsafe_allow_html=True)
                st.markdown("### Feedback")
                st.markdown(analysis["feedback"])

                if analysis["warnings"]:
                    st.warning(f"⚠️ {len(analysis['warnings'])} warnings found")
                if analysis["errors"]:
                    st.error(f"❌ {len(analysis['errors'])} critical issues")

                save_review(st.session_state.user_id, code, analysis["feedback"], language)
                st.toast("✅ Review saved to your history!")
                st.markdown(get_download_link(analysis["feedback"], "feedback.txt"), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ Error during analysis: {e}")

    # 📘 Explain Code
    if st.button("Explain Code", type="secondary") and code:
        with st.spinner("Explaining your code..."):
            try:
                explanation = explain_code(code, language)
                st.subheader("🧠 Code Explanation")
                st.markdown(explanation)
            except Exception as e:
                st.error(f"⚠️ Error during explanation: {e}")

    # 📝 Review History
    st.subheader("My Review History")
    try:
        reviews = get_user_reviews(st.session_state.user_id)
        if reviews:
            for review in reviews:
                with st.expander(f"{review['language'].upper()} - {review['timestamp'].split('.')[0]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Code**")
                        st.code(review['code'][:300] + ("..." if len(review['code']) > 300 else ""))
                    with col2:
                        st.markdown("**Feedback**")
                        st.markdown(review['feedback'][:500] + ("..." if len(review['feedback']) > 500 else ""))
        else:
            st.info("No reviews yet. Analyze some code to get started!")
    except Exception as e:
        st.error(f"⚠️ Error fetching review history: {e}")


# =============================
# 📊 Dashboard Page
# =============================
def show_dashboard(user_id):
    st.title("📊 Review Analytics")
    try:
        reviews = get_user_reviews(user_id)
        if not reviews:
            st.info("No data to display yet.")
        else:
            df = pd.DataFrame(reviews)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            st.metric("Total Reviews", len(df))
            st.metric("Languages Used", df['language'].nunique())

            lang_chart = alt.Chart(df).mark_bar().encode(
                x='language',
                y='count()',
                color='language'
            ).properties(title="Languages Reviewed")

            time_chart = alt.Chart(df).mark_line().encode(
                x='timestamp',
                y='count()'
            ).properties(title="Review Activity Over Time")

            st.altair_chart(lang_chart, use_container_width=True)
            st.altair_chart(time_chart, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Error loading dashboard: {e}")


# =============================
# 🚀 App Flow
# =============================
init_app()
if not st.session_state.logged_in:
    auth_section()
    st.stop()
else:
    # ✅ Changed this line
    st.sidebar.header(f"Welcome, {st.session_state.get('username', 'User')}")
    page = st.sidebar.radio("Navigate", ["Home", "Dashboard"])
    if page == "Home":
        main_app()
    elif page == "Dashboard":
        show_dashboard(st.session_state.user_id)


# =============================
# 🎨 UI Enhancements
# =============================
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)  # keep your custom CSS
