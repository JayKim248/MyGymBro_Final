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
    .form-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem auto;
        max-width: 600px;
        border-left: 4px solid #4ecdc4;
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
if "signup_stage" not in st.session_state:
    st.session_state["signup_stage"] = 1  # 1 = 단계 1, 2 = 단계 2
if "signup_form_step" not in st.session_state:
    st.session_state["signup_form_step"] = 1  # 1, 2, or 3 for the form steps in stage 2
if "temp_user_data" not in st.session_state:
    st.session_state["temp_user_data"] = {}  # Temporary storage for stage 2 data

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

def create_user_basic(email, password, first_name, last_name):
    """Create a basic user account with minimal information."""
    users = load_users()
    
    if email in users:
        return False, "Email already exists"
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    # Create minimal user data
    user_data = {
        "email": email,
        "password": hash_password(password),
        "first_name": first_name,
        "last_name": last_name,
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

def update_user_profile(email, updated_data):
    """Update user profile with additional information."""
    users = load_users()
    if email in users:
        # Convert height and weight if provided
        if 'height_feet' in updated_data and 'height_inches' in updated_data:
            height_feet = updated_data['height_feet']
            height_inches = updated_data['height_inches']
            updated_data['height_cm'] = height_feet * 30.48 + height_inches * 2.54
        
        if 'weight_lbs' in updated_data:
            weight_lbs = updated_data['weight_lbs']
            updated_data['weight_kg'] = weight_lbs * 0.453592
        
        # Update the user data
        users[email].update(updated_data)
        save_users(users)
        return True, users[email]
    return False, None

# Main UI
st.markdown('<h1 class="main-header">💪 MyGymBro</h1>', unsafe_allow_html=True)

# 단계 1: 기본 정보 입력
if st.session_state["signup_stage"] == 1:
    st.markdown('<h2 style="text-align: center; color: #666;">Join the Fitness Community!</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("### 🆕 Step 1: Create Your Account")
        
        with st.form("signup_form_stage1"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("👤 First Name", placeholder="Enter your first name", key="stage1_first_name")
            with col2:
                last_name = st.text_input("👤 Last Name", placeholder="Enter your last name", key="stage1_last_name")
            
            email = st.text_input("📧 Email Address", placeholder="Enter your email address", key="stage1_email")
            
            col3, col4 = st.columns(2)
            with col3:
                password = st.text_input("🔒 Password", type="password", placeholder="Create a password", key="stage1_password")
            with col4:
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password", key="stage1_confirm_password")
            
            # Terms and conditions
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="stage1_terms")
            
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
                    result = create_user_basic(email, password, first_name, last_name)
                    if len(result) == 3:  # Success case
                        success, message, user_data = result
                        if success:
                            # Store basic user data and move to stage 2
                            st.session_state["user_email"] = email
                            st.session_state["temp_user_data"] = user_data.copy()
                            st.session_state["signup_stage"] = 2
                            st.session_state["signup_form_step"] = 1
                            st.rerun()
                    else:  # Error case
                        success, message = result
                        st.error(f"❌ {message}")
        
        st.markdown("---")
        st.markdown("### 🔐 Already have an account?")
        if st.button("Sign In", use_container_width=True, key="stage1_signin"):
            st.switch_page("pages/1_login.py")
        
        st.markdown("</div>", unsafe_allow_html=True)

# 단계 2: 추가 정보 순차 입력
elif st.session_state["signup_stage"] == 2:
    st.markdown('<h2 style="text-align: center; color: #666;">Complete Your Profile</h2>', unsafe_allow_html=True)
    
    # Progress bar (위쪽 영역)
    total_steps = 3
    current_step = st.session_state["signup_form_step"]
    progress = current_step / total_steps
    st.progress(progress)
    st.markdown(f"**Step {current_step} of {total_steps}**")
    st.markdown("---")
    
    # 입력 폼 (아래쪽 영역)
    with st.container():
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        # 폼 1: Feet, Inches, Weight
        if current_step == 1:
            st.markdown("### 📏 Step 1: Body Measurements")
            with st.form("form_step1"):
                st.markdown("**Height:**")
                col_height1, col_height2 = st.columns(2)
                with col_height1:
                    height_feet = st.number_input("Feet", min_value=3, max_value=8, value=5, key="form1_feet")
                with col_height2:
                    height_inches = st.number_input("Inches", min_value=0, max_value=11, value=9, key="form1_inches")
                
                weight_lbs = st.number_input("⚖️ Weight (lbs)", min_value=66, max_value=440, value=154, key="form1_weight")
                
                next_button = st.form_submit_button("➡️ Next", use_container_width=True)
                
                if next_button:
                    st.session_state["temp_user_data"]["height_feet"] = height_feet
                    st.session_state["temp_user_data"]["height_inches"] = height_inches
                    st.session_state["temp_user_data"]["weight_lbs"] = weight_lbs
                    st.session_state["signup_form_step"] = 2
                    st.rerun()
        
        # 폼 2: Lifestyle, Exercise Experience, Current Fitness Level
        elif current_step == 2:
            st.markdown("### 🏃 Step 2: Lifestyle & Fitness Level")
            with st.form("form_step2"):
                lifestyle = st.selectbox(
                    "🏠 Lifestyle",
                    ["Lying down 15+ hours", "Almost no movement at home", "Student or office worker", "Active", "Very active"],
                    key="form2_lifestyle"
                )
                
                exercise_experience = st.selectbox(
                    "💪 Exercise Experience",
                    ["Beginner", "1-3 years", "3-5 years intermediate", "5+ years advanced", "10+ years expert"],
                    key="form2_experience"
                )
                
                # Show PR fields if experience is more than 1 year
                show_pr_fields = exercise_experience != "Beginner"
                
                if show_pr_fields:
                    st.markdown("---")
                    st.markdown("### 💪 Personal Records (PR)")
                    st.markdown("*Please enter your current personal records (optional but recommended)*")
                    
                    col_bench, col_squat = st.columns(2)
                    with col_bench:
                        bench_pr = st.number_input(
                            "🏋️ Bench Press PR (lbs)",
                            min_value=0.0,
                            max_value=1000.0,
                            value=0.0,
                            step=5.0,
                            key="form2_bench_pr",
                            help="Enter your 1-rep max or best bench press weight"
                        )
                    
                    with col_squat:
                        squat_pr = st.number_input(
                            "🦵 Squat PR (lbs)",
                            min_value=0.0,
                            max_value=1000.0,
                            value=0.0,
                            step=5.0,
                            key="form2_squat_pr",
                            help="Enter your 1-rep max or best squat weight"
                        )
                    
                    st.markdown("---")
                    st.markdown("### 🏃 Ridley Cross Country Run Time")
                    time_input = st.text_input(
                        "⏱️ Ridley Cross Country Run 3km Time (MM:SS or minutes)",
                        value="",
                        key="form2_ridley_time",
                        help="Enter your best 3km time (e.g., 12:30 for 12 minutes 30 seconds, or 12.5 for 12.5 minutes)",
                        placeholder="e.g., 12:30 or 12.5"
                    )
                    
                    # Parse time input
                    ridley_time_minutes = 0.0
                    if time_input:
                        try:
                            if ":" in time_input:
                                # Format: MM:SS
                                parts = time_input.split(":")
                                minutes = int(parts[0])
                                seconds = int(parts[1]) if len(parts) > 1 else 0
                                ridley_time_minutes = minutes + (seconds / 60.0)
                            else:
                                # Format: decimal minutes
                                ridley_time_minutes = float(time_input)
                        except:
                            ridley_time_minutes = 0.0
                
                fitness_level = st.selectbox(
                    "🏃 Current Fitness Level",
                    ["Very poor", "Poor", "Below average", "Average", "Above average", "Good", "Very good"],
                    key="form2_fitness"
                )
                
                col_back, col_next = st.columns(2)
                with col_back:
                    back_button = st.form_submit_button("⬅️ Back", use_container_width=True)
                with col_next:
                    next_button = st.form_submit_button("➡️ Next", use_container_width=True)
                
                if back_button:
                    st.session_state["signup_form_step"] = 1
                    st.rerun()
                elif next_button:
                    st.session_state["temp_user_data"]["lifestyle"] = lifestyle
                    st.session_state["temp_user_data"]["exercise_experience"] = exercise_experience
                    st.session_state["temp_user_data"]["fitness_level"] = fitness_level
                    
                    # Save PR data if shown
                    if show_pr_fields:
                        st.session_state["temp_user_data"]["bench_press_pr"] = bench_pr
                        st.session_state["temp_user_data"]["squat_pr"] = squat_pr
                        st.session_state["temp_user_data"]["ridley_crosscountry_time"] = ridley_time_minutes
                    else:
                        # Set PR data to 0 if Beginner
                        st.session_state["temp_user_data"]["bench_press_pr"] = 0.0
                        st.session_state["temp_user_data"]["squat_pr"] = 0.0
                        st.session_state["temp_user_data"]["ridley_crosscountry_time"] = 0.0
                    
                    st.session_state["signup_form_step"] = 3
                    st.rerun()
        
        # 폼 3: Sports/Activities, Sports Frequency
        elif current_step == 3:
            st.markdown("### 🏀 Step 3: Sports & Activities")
            with st.form("form_step3"):
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
                    key="form3_sports",
                    help="Select all sports or activities you participate in regularly"
                )
                
                exercise_frequency = st.selectbox(
                    "📅 Sports Frequency (How often do you play sports and activity)",
                    ["None", "1x/week", "2x/week", "3x/week", "4x/week", "5x/week", "6x/week", "7x/week"],
                    key="form3_frequency"
                )
                
                # Add default values for age and gender if not set
                if "age" not in st.session_state["temp_user_data"]:
                    col_age, col_gender = st.columns(2)
                    with col_age:
                        age = st.number_input("🎂 Age", min_value=13, max_value=100, value=20, key="form3_age")
                    with col_gender:
                        gender = st.selectbox("⚥ Gender", ["Male", "Female", "Other"], key="form3_gender")
                    st.session_state["temp_user_data"]["age"] = age
                    st.session_state["temp_user_data"]["gender"] = gender
                else:
                    age = st.session_state["temp_user_data"].get("age", 20)
                    gender = st.session_state["temp_user_data"].get("gender", "Male")
                
                col_back, col_complete = st.columns(2)
                with col_back:
                    back_button = st.form_submit_button("⬅️ Back", use_container_width=True)
                with col_complete:
                    complete_button = st.form_submit_button("✅ Complete Profile", use_container_width=True)
                
                if back_button:
                    st.session_state["signup_form_step"] = 2
                    st.rerun()
                elif complete_button:
                    # Save all additional information
                    st.session_state["temp_user_data"]["exercise_frequency"] = exercise_frequency
                    st.session_state["temp_user_data"]["sports_activities"] = sports_activities
                    
                    # Update user profile with all collected data
                    success, updated_user_data = update_user_profile(
                        st.session_state["user_email"],
                        st.session_state["temp_user_data"]
                    )
                    
                    if success:
                        # Automatically log in the user
                        st.session_state["authenticated"] = True
                        st.session_state["user_data"] = updated_user_data
                        st.success("✅ Profile completed successfully!")
                        st.balloons()
                        st.info("🔄 Redirecting to main app...")
                        
                        # Reset signup state
                        st.session_state["signup_stage"] = 1
                        st.session_state["signup_form_step"] = 1
                        st.session_state["temp_user_data"] = {}
                        
                        st.switch_page("pages/3_main_app.py")
                    else:
                        st.error("❌ Failed to save profile. Please try again.")
        
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
