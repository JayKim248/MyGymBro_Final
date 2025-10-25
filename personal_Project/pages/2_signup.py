import streamlit as st
import json
from pathlib import Path
import hashlib
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Sign Up",
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
        max-width: 500px;
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

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def create_user(email, password, first_name, last_name, age, gender, fitness_level, height_feet, height_inches, weight_lbs, lifestyle, exercise_experience, exercise_frequency, sports_activities):
    """Create a new user account."""
    users = load_users()
    
    if email in users:
        return False, "Email already exists"
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    # Convert height to cm and weight to kg
    height_cm = height_feet * 30.48 + height_inches * 2.54
    weight_kg = weight_lbs * 0.453592
    
    user_data = {
        "email": email,
        "password": hash_password(password),
        "first_name": first_name,
        "last_name": last_name,
        "age": age,
        "gender": gender,
        "fitness_level": fitness_level,
        "height_cm": height_cm,
        "height_feet": height_feet,
        "height_inches": height_inches,
        "weight_kg": weight_kg,
        "weight_lbs": weight_lbs,
        "lifestyle": lifestyle,
        "exercise_experience": exercise_experience,
        "exercise_frequency": exercise_frequency,
        "sports_activities": sports_activities,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "workout_history": [],
        "preferences": {
            "language": "English",
            "notifications": True,
            "theme": "light"
        }
    }
    
    users[email] = user_data
    save_users(users)
    return True, "Account created successfully", user_data

def login_user(email, password):
    """Login user and set session state."""
    users = load_users()
    if email in users and users[email]['password'] == hash_password(password):
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = email
        st.session_state["user_data"] = users[email]
        return True
    return False

# Main UI
st.markdown('<h1 class="main-header">💪 MyGymBro</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Join the Fitness Community!</h2>', unsafe_allow_html=True)

# Sign-up form
with st.container():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    st.markdown("### 🆕 Create Your Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("👤 First Name", placeholder="Enter your first name")
        with col2:
            last_name = st.text_input("👤 Last Name", placeholder="Enter your last name")
        
        email = st.text_input("📧 Email Address", placeholder="Enter your email address")
        
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
        with col4:
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        col5, col6 = st.columns(2)
        with col5:
            age = st.number_input("🎂 Age", min_value=13, max_value=100, value=20)
        with col6:
            gender = st.selectbox("⚥ Gender", ["Male", "Female", "Other"])
        
        # Height input
        st.markdown("**📏 Height:**")
        col_height1, col_height2 = st.columns(2)
        with col_height1:
            height_feet = st.number_input("Feet", min_value=3, max_value=8, value=5, key="signup_feet")
        with col_height2:
            height_inches = st.number_input("Inches", min_value=0, max_value=11, value=9, key="signup_inches")
        
        # Weight input
        weight_lbs = st.number_input("⚖️ Weight (lbs)", min_value=66, max_value=440, value=154, key="signup_weight")
        
        # Lifestyle
        lifestyle = st.selectbox(
            "🏠 Lifestyle",
            ["Lying down 15+ hours", "Almost no movement at home", "Student or office worker", "Active", "Very active"],
            key="signup_lifestyle"
        )
        
        col7, col8 = st.columns(2)
        with col7:
            exercise_experience = st.selectbox(
                "💪 Exercise Experience",
                ["Beginner", "1-3 years", "3-5 years intermediate", "5+ years advanced", "10+ years expert"],
                key="signup_experience"
            )
            exercise_frequency = st.selectbox(
                "📅 Exercise Frequency",
                ["None", "1x/week", "2x/week", "3x/week", "4x/week", "5x/week", "6x/week", "7x/week"],
                key="signup_frequency"
            )
        with col8:
            fitness_level = st.selectbox(
                "🏃 Current Fitness Level",
                ["Very poor", "Poor", "Below average", "Average", "Above average", "Good", "Very good"],
                key="signup_fitness"
            )
        
        # Sports/Activities section
        sports_activities = st.multiselect(
            "🏀 Sports/Activities",
            [
                "Basketball", "Soccer", "Tennis", "Swimming", "Running", "Cycling", 
                "Volleyball", "Baseball", "Football", "Hockey", "Track & Field", 
                "Wrestling", "Boxing", "Martial Arts", "Dance", "Yoga", "Pilates",
                "Rock Climbing", "Gymnastics", "Lacrosse", "Rugby", "Golf", 
                "Badminton", "Table Tennis", "Skiing", "Snowboarding", "Surfing",
                "Rowing", "Erg", "None - Just gym workouts", "Other"
            ],
            key="signup_sports",
            help="Select all sports or activities you participate in regularly"
        )
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        col7, col8 = st.columns([1, 1])
        with col7:
            signup_button = st.form_submit_button("🚀 Create Account", use_container_width=True)
        with col8:
            if st.form_submit_button("🔐 Login", use_container_width=True):
                st.switch_page("pages/1_login.py")
        
        if signup_button:
            if not all([first_name, last_name, email, password, confirm_password]):
                st.error("❌ Please fill in all required fields.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif not agree_terms:
                st.error("❌ Please agree to the Terms of Service and Privacy Policy.")
            else:
                result = create_user(email, password, first_name, last_name, age, gender, fitness_level, 
                                   height_feet, height_inches, weight_lbs, lifestyle, exercise_experience, 
                                   exercise_frequency, sports_activities)
                if len(result) == 3:  # Success case with user_data
                    success, message, user_data = result
                    if success:
                        # Automatically log in the user
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = email
                        st.session_state["user_data"] = user_data
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("🔄 Redirecting to main app...")
                        st.switch_page("pages/3_main_app.py")
                else:  # Error case
                    success, message = result
                    st.error(f"❌ {message}")
    
    st.markdown("---")
    st.markdown("### 🔐 Already have an account?")
    st.markdown("Sign in to access your personalized workout routines!")
    
    if st.button("Sign In", use_container_width=True):
        st.switch_page("pages/1_login.py")
    
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
