import streamlit as st
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Update Profile",
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
</style>
""", unsafe_allow_html=True)

# Check authentication
if not st.session_state.get("authenticated", False):
    st.warning("🔐 Please log in to update your profile")
    if st.button("Go to Login", use_container_width=True):
        st.switch_page("pages/1_login.py")
    st.stop()

# Initialize session state for update form
if "update_form_step" not in st.session_state:
    st.session_state["update_form_step"] = 1
if "temp_update_data" not in st.session_state:
    st.session_state["temp_update_data"] = {}

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
        
        # Update session state
        st.session_state["user_data"] = users[email]
        return True, users[email]
    return False, None

# Get current user data
user_email = st.session_state.get("user_email")
user_data = st.session_state.get("user_data", {})

# Main UI
st.markdown('<h1 class="main-header">💪 Update Your Profile</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Update Your Information</h2>', unsafe_allow_html=True)

# Progress bar
total_steps = 3
current_step = st.session_state["update_form_step"]
progress = current_step / total_steps
st.progress(progress)
st.markdown(f"**Step {current_step} of {total_steps}**")
st.markdown("---")

# Helper function to get default values from user data
def get_default_height_feet():
    if 'height_cm' in user_data:
        total_inches = user_data['height_cm'] / 2.54
        return int(total_inches // 12)
    elif 'height_feet' in user_data:
        return user_data['height_feet']
    return 5

def get_default_height_inches():
    if 'height_cm' in user_data:
        total_inches = user_data['height_cm'] / 2.54
        return int(total_inches % 12)
    elif 'height_inches' in user_data:
        return user_data['height_inches']
    return 9

# Input form
with st.container():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    
    # Form 1: Feet, Inches, Weight
    if current_step == 1:
        st.markdown("### 📏 Step 1: Body Measurements")
        with st.form("update_form_step1"):
            st.markdown("**Height:**")
            col_height1, col_height2 = st.columns(2)
            with col_height1:
                height_feet = st.number_input(
                    "Feet", 
                    min_value=3, 
                    max_value=8, 
                    value=get_default_height_feet(), 
                    key="update_form1_feet"
                )
            with col_height2:
                height_inches = st.number_input(
                    "Inches", 
                    min_value=0, 
                    max_value=11, 
                    value=get_default_height_inches(), 
                    key="update_form1_inches"
                )
            
            weight_lbs = st.number_input(
                "⚖️ Weight (lbs)", 
                min_value=66, 
                max_value=440, 
                value=int(user_data.get('weight_lbs', 154)), 
                key="update_form1_weight"
            )
            
            next_button = st.form_submit_button("➡️ Next", use_container_width=True)
            
            if next_button:
                st.session_state["temp_update_data"]["height_feet"] = height_feet
                st.session_state["temp_update_data"]["height_inches"] = height_inches
                st.session_state["temp_update_data"]["weight_lbs"] = weight_lbs
                st.session_state["update_form_step"] = 2
                st.rerun()
    
    # Form 2: Lifestyle, Exercise Experience, Current Fitness Level
    elif current_step == 2:
        st.markdown("### 🏃 Step 2: Lifestyle & Fitness Level")
        with st.form("update_form_step2"):
            lifestyle_options = ["Lying down 15+ hours", "Almost no movement at home", "Student or office worker", "Active", "Very active"]
            lifestyle_index = lifestyle_options.index(user_data.get('lifestyle', 'Student or office worker')) if user_data.get('lifestyle') in lifestyle_options else 2
            lifestyle = st.selectbox(
                "🏠 Lifestyle",
                lifestyle_options,
                index=lifestyle_index,
                key="update_form2_lifestyle"
            )
            
            experience_options = ["Beginner", "1-3 years", "3-5 years intermediate", "5+ years advanced", "10+ years expert"]
            experience_index = experience_options.index(user_data.get('exercise_experience', 'Beginner')) if user_data.get('exercise_experience') in experience_options else 0
            exercise_experience = st.selectbox(
                "💪 Exercise Experience",
                experience_options,
                index=experience_index,
                key="update_form2_experience"
            )
            
            # Show PR fields if experience is more than 1 year
            show_pr_fields = exercise_experience != "Beginner"
            ridley_time_minutes = 0.0  # Initialize variable
            
            if show_pr_fields:
                st.markdown("---")
                st.markdown("### 💪 Personal Records (PR)")
                st.markdown("*Please enter your current personal records (optional but recommended)*")
                
                col_bench, col_squat = st.columns(2)
                with col_bench:
                    temp_data = st.session_state["temp_update_data"]
                    bench_pr = st.number_input(
                        "🏋️ Bench Press PR (lbs)",
                        min_value=0.0,
                        max_value=1000.0,
                        value=float(temp_data.get('bench_press_pr', user_data.get('bench_press_pr', 0.0))),
                        step=5.0,
                        key="update_form2_bench_pr",
                        help="Enter your 1-rep max or best bench press weight"
                    )
                
                with col_squat:
                    squat_pr = st.number_input(
                        "🦵 Squat PR (lbs)",
                        min_value=0.0,
                        max_value=1000.0,
                        value=float(temp_data.get('squat_pr', user_data.get('squat_pr', 0.0))),
                        step=5.0,
                        key="update_form2_squat_pr",
                        help="Enter your 1-rep max or best squat weight"
                    )
                
                st.markdown("---")
                st.markdown("### 🏃 Ridley Cross Country Run Time")
                temp_data = st.session_state["temp_update_data"]
                # Get existing time or default to 0
                existing_time = temp_data.get('ridley_crosscountry_time', user_data.get('ridley_crosscountry_time', 0.0))
                
                # Format time input - allow minutes:seconds or decimal minutes
                time_input = st.text_input(
                    "⏱️ Ridley Cross Country Run 3km Time (MM:SS or minutes)",
                    value=f"{int(existing_time)}:{int((existing_time % 1) * 60):02d}" if existing_time > 0 else "",
                    key="update_form2_ridley_time",
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
            
            fitness_options = ["Very poor", "Poor", "Below average", "Average", "Above average", "Good", "Very good"]
            fitness_index = fitness_options.index(user_data.get('fitness_level', 'Average')) if user_data.get('fitness_level') in fitness_options else 3
            fitness_level = st.selectbox(
                "🏃 Current Fitness Level",
                fitness_options,
                index=fitness_index,
                key="update_form2_fitness"
            )
            
            col_back, col_next = st.columns(2)
            with col_back:
                back_button = st.form_submit_button("⬅️ Back", use_container_width=True)
            with col_next:
                next_button = st.form_submit_button("➡️ Next", use_container_width=True)
            
            if back_button:
                st.session_state["update_form_step"] = 1
                st.rerun()
            elif next_button:
                st.session_state["temp_update_data"]["lifestyle"] = lifestyle
                st.session_state["temp_update_data"]["exercise_experience"] = exercise_experience
                st.session_state["temp_update_data"]["fitness_level"] = fitness_level
                
                # Save PR data if shown
                if show_pr_fields:
                    st.session_state["temp_update_data"]["bench_press_pr"] = bench_pr
                    st.session_state["temp_update_data"]["squat_pr"] = squat_pr
                    st.session_state["temp_update_data"]["ridley_crosscountry_time"] = ridley_time_minutes
                else:
                    # Clear PR data if user changed to Beginner
                    st.session_state["temp_update_data"]["bench_press_pr"] = 0.0
                    st.session_state["temp_update_data"]["squat_pr"] = 0.0
                    st.session_state["temp_update_data"]["ridley_crosscountry_time"] = 0.0
                
                st.session_state["update_form_step"] = 3
                st.rerun()
    
    # Form 3: Sports/Activities, Sports Frequency, Age, Gender
    elif current_step == 3:
        st.markdown("### 🏀 Step 3: Sports & Activities")
        with st.form("update_form_step3"):
            sports_options = [
                "Basketball", "Soccer", "Tennis", "Swimming", "Running", "Cycling", 
                "Volleyball", "Baseball", "Football", "Hockey", "Track & Field", 
                "Wrestling", "Boxing", "Martial Arts", "Dance", "Yoga", "Pilates",
                "Rock Climbing", "Gymnastics", "Lacrosse", "Rugby", "Golf", 
                "Badminton", "Table Tennis", "Skiing", "Snowboarding", "Surfing",
                "Rowing", "Erg", "None - Just gym workouts", "Other"
            ]
            current_sports = user_data.get('sports_activities', [])
            sports_activities = st.multiselect(
                "🏀 Sports/Activities",
                sports_options,
                default=current_sports,
                key="update_form3_sports",
                help="Select all sports or activities you participate in regularly"
            )
            
            frequency_options = ["None", "1x/week", "2x/week", "3x/week", "4x/week", "5x/week", "6x/week", "7x/week"]
            frequency_index = frequency_options.index(user_data.get('exercise_frequency', '3x/week')) if user_data.get('exercise_frequency') in frequency_options else 3
            exercise_frequency = st.selectbox(
                "📅 Sports Frequency (How often do you play sports and activity)",
                frequency_options,
                index=frequency_index,
                key="update_form3_frequency"
            )
            
            col_age, col_gender = st.columns(2)
            with col_age:
                age = st.number_input(
                    "🎂 Age", 
                    min_value=13, 
                    max_value=100, 
                    value=int(user_data.get('age', 20)), 
                    key="update_form3_age"
                )
            with col_gender:
                gender_options = ["Male", "Female", "Other"]
                gender_index = gender_options.index(user_data.get('gender', 'Male')) if user_data.get('gender') in gender_options else 0
                gender = st.selectbox(
                    "⚥ Gender", 
                    gender_options,
                    index=gender_index,
                    key="update_form3_gender"
                )
            
            col_back, col_save = st.columns(2)
            with col_back:
                back_button = st.form_submit_button("⬅️ Back", use_container_width=True)
            with col_save:
                save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            if back_button:
                st.session_state["update_form_step"] = 2
                st.rerun()
            elif save_button:
                # Collect all data from temp and current form
                all_update_data = st.session_state["temp_update_data"].copy()
                all_update_data["exercise_frequency"] = exercise_frequency
                all_update_data["sports_activities"] = sports_activities
                all_update_data["age"] = age
                all_update_data["gender"] = gender
                
                # Update user profile with all collected data
                success, updated_user_data = update_user_profile(
                    user_email,
                    all_update_data
                )
                
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.balloons()
                    st.info("🔄 Redirecting to main app...")
                    
                    # Reset update form state
                    st.session_state["update_form_step"] = 1
                    st.session_state["temp_update_data"] = {}
                    
                    # Small delay before redirect
                    import time
                    time.sleep(1)
                    st.switch_page("pages/3_main_app.py")
                else:
                    st.error("❌ Failed to update profile. Please try again.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Back to main app button
st.markdown("---")
if st.button("🔙 Back to Main App", use_container_width=True):
    # Reset form state
    st.session_state["update_form_step"] = 1
    st.session_state["temp_update_data"] = {}
    st.switch_page("pages/3_main_app.py")

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

