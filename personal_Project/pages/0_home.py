import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Home",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .hero-section {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 3rem;
        border-radius: 20px;
        margin: 2rem auto;
        max-width: 800px;
        text-align: center;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #4ecdc4;
    }
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff5252, #26c6da);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Main UI
st.markdown('<h1 class="main-header">💪 MyGymBro</h1>', unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero-section">
    <h2 style="color: #333; margin-bottom: 1rem;">Your AI-Powered Fitness Companion</h2>
    <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
        Get personalized workout routines, track your progress, and achieve your fitness goals with the power of AI.
    </p>
    <p style="font-size: 1rem; color: #888;">
        Perfect for students who want to maximize their gym time with smart, efficient workouts.
    </p>
</div>
""", unsafe_allow_html=True)

# Features section
st.markdown("### 🌟 Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 AI Workout Planning</h3>
        <p>Get personalized workout routines based on your fitness level, available equipment, and goals.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Progress Tracking</h3>
        <p>Track your workouts, monitor your progress, and get insights into your fitness journey.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🌍 Multi-Language</h3>
        <p>Available in English, French, Korean, Mandarin, and Spanish for global accessibility.</p>
    </div>
    """, unsafe_allow_html=True)

# Action buttons
st.markdown("---")
st.markdown("### 🚀 Get Started")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔐 Login to MyGymBro", use_container_width=True):
        st.switch_page("pages/1_login.py")

with col2:
    if st.button("🆕 Create New Account", use_container_width=True):
        st.switch_page("pages/2_signup.py")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem;'>
        💪 MyGymBro - Student Gym Routine Builder<br>
        <small>Powered by AI • Built for Students • Free to Use</small>
    </div>
    """, 
    unsafe_allow_html=True
)
