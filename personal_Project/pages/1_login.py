import streamlit as st
import json
from pathlib import Path
import hashlib
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Login",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .auth-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem auto;
        max-width: 400px;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff5252, #26c6da);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f44336;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_data" not in st.session_state:
    st.session_state["user_data"] = None

# Data directory setup
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"

def load_users():
    """Load users from JSON file."""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash."""
    return hash_password(password) == hashed

def authenticate_user(email, password):
    """Authenticate user with email and password."""
    users = load_users()
    if email in users:
        if verify_password(password, users[email]['password']):
            return users[email]
    return None

def login_user(email, password):
    """Login user and set session state."""
    user_data = authenticate_user(email, password)
    if user_data:
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = email
        st.session_state["user_data"] = user_data
        return True
    return False

# Main UI
st.markdown('<h1 class="main-header">💪 MyGymBro</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Welcome Back!</h2>', unsafe_allow_html=True)

# Login form
with st.container():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    st.markdown("### 🔐 Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
        with col2:
            if st.form_submit_button("🆕 Sign Up", use_container_width=True):
                st.switch_page("pages/2_signup.py")
        
        if login_button:
            if email and password:
                if login_user(email, password):
                    st.success("✅ Login successful! Redirecting to main app...")
                    st.balloons()
                    st.switch_page("pages/3_main_app.py")
                else:
                    st.error("❌ Invalid email or password. Please try again.")
            else:
                st.error("❌ Please fill in all fields.")
    
    st.markdown("---")
    st.markdown("### 🆕 New to MyGymBro?")
    st.markdown("Create an account to get personalized workout routines and track your fitness journey!")
    
    if st.button("Create New Account", use_container_width=True):
        st.switch_page("pages/2_signup.py")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        💪 MyGymBro - Student Gym Routine Builder<br>
        <small>Your AI-powered fitness companion</small>
    </div>
    """, 
    unsafe_allow_html=True
)

# Toronto Blue Jays logo - Clickable for auto-login
st.markdown("---")
st.markdown("### Toronto Blue Jays")

# Display Blue Jays logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("Images/Toronto_Blue_Jays_Logo.jpg", width=200)
    except:
        st.markdown("**TORONTO BLUE JAYS**")

# Create a clickable Blue Jays section
if st.button(
    """
    TORONTO
    BLUE JAYS
    
    MLB Team
    
    Click to login as Blue Jays fan
    """,
    use_container_width=True,
    help="Click to automatically login with Blue Jays fan profile"
):
    # Create Blue Jays fan user data
    blue_jays_user_data = {
        "email": "bluejays.fan@mygymbro.com",
        "password": hash_password("bluejays2024"),
        "first_name": "Blue Jays",
        "last_name": "Fan",
        "age": 16,
        "gender": "Male",
        "fitness_level": "Advanced",
        "height_cm": 175,  # 5'9"
        "height_feet": 5,
        "height_inches": 9,
        "weight_kg": 70,   # ~154 lbs
        "weight_lbs": 154,
        "lifestyle": "Active",
        "exercise_experience": "3-5 years intermediate",
        "exercise_frequency": "5x/week",
        "sports_activities": ["Baseball"],
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "workout_history": [],
        "preferences": {
            "language": "English",
            "notifications": True,
            "theme": "light"
        }
    }
    
    # Save the Blue Jays user to the users file
    users = load_users()
    users["bluejays.fan@mygymbro.com"] = blue_jays_user_data
    save_users(users)
    
    # Log in the Blue Jays fan
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = "bluejays.fan@mygymbro.com"
    st.session_state["user_data"] = blue_jays_user_data
    
    st.success("Welcome, Blue Jays Fan! Logging you in...")
    st.balloons()
    st.switch_page("pages/3_main_app.py")

# Clash Royale section
st.markdown("---")
st.markdown("### Clash Royale")

# Display Clash Royale logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("Images/Clash_Royale_Logo.png", width=200)
    except:
        st.markdown("**CLASH ROYALE**")

# Create a clickable Clash Royale section
if st.button(
    """
    CLASH ROYALE
    
    Mobile Game
    
    Click to login as Clash Royale player
    """,
    use_container_width=True,
    help="Click to automatically login with Clash Royale player profile"
):
    # Create Clash Royale player user data
    clash_royale_user_data = {
        "email": "clashroyale.player@mygymbro.com",
        "password": hash_password("clashroyale2024"),
        "first_name": "Clash",
        "last_name": "Royale",
        "age": 18,
        "gender": "Male",
        "fitness_level": "Intermediate",
        "height_cm": 180,  # 5'11"
        "height_feet": 5,
        "height_inches": 11,
        "weight_kg": 75,   # ~165 lbs
        "weight_lbs": 165,
        "lifestyle": "Student or office worker",
        "exercise_experience": "1-2 years beginner",
        "exercise_frequency": "3x/week",
        "sports_activities": ["Gaming"],
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "workout_history": [],
        "preferences": {
            "language": "English",
            "notifications": True,
            "theme": "light"
        }
    }
    
    # Save the Clash Royale user to the users file
    users = load_users()
    users["clashroyale.player@mygymbro.com"] = clash_royale_user_data
    save_users(users)
    
    # Log in the Clash Royale player
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = "clashroyale.player@mygymbro.com"
    st.session_state["user_data"] = clash_royale_user_data
    
    st.success("Welcome, Clash Royale Player! Logging you in...")
    st.balloons()
    st.switch_page("pages/3_main_app.py")

# Style the buttons to look like the team/game logos
st.markdown("""
<style>
    .stButton > button {
        background: linear-gradient(135deg, #1E3A8A, #DC2626) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 2rem 1rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        text-align: center !important;
        line-height: 1.4 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        transition: transform 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
    }
    
    /* Clash Royale button styling */
    .stButton:nth-of-type(2) > button {
        background: linear-gradient(135deg, #FFD700, #FF6B35) !important;
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)
