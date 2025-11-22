import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Custom Workout for U",
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
    st.warning("🔐 Please log in to create a custom workout")
    if st.button("Go to Login", use_container_width=True):
        st.switch_page("pages/1_login.py")
    st.stop()

# Initialize session state for custom workout form
if "custom_workout_step" not in st.session_state:
    st.session_state["custom_workout_step"] = 1
if "temp_custom_workout_data" not in st.session_state:
    st.session_state["temp_custom_workout_data"] = {}

# Get user data
user_data = st.session_state.get("user_data", {})
age = user_data.get("age", 20)
gender = user_data.get("gender", "Male")
fitness_level = user_data.get("fitness_level", "Average")
exercise_frequency = user_data.get("exercise_frequency", "3x/week")
sports_activities = user_data.get("sports_activities", [])

# Main UI
st.markdown('<h1 class="main-header">✨ Custom Workout for U</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Tell us about your ideal workout</h2>', unsafe_allow_html=True)

# Progress bar
total_steps = 3
current_step = st.session_state["custom_workout_step"]
progress = current_step / total_steps
st.progress(progress)
st.markdown(f"**Step {current_step} of {total_steps}**")
st.markdown("---")

# Input form
with st.container():
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    
    # Step 1: Basic Preferences
    if current_step == 1:
        st.markdown("### 📋 Step 1: Basic Workout Preferences")
        
        # Workout days selection (outside form so buttons work properly)
        temp_data = st.session_state["temp_custom_workout_data"]
        st.markdown("**📅 What day do you want to workout?**")
        st.markdown("*Click the buttons below to select your workout days*")
        
        # Get previously selected days
        previously_selected = temp_data.get('workout_days', [])
        
        # Create 7 buttons for each day of the week
        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        day_cols = st.columns(7)
        selected_workout_days = previously_selected.copy()  # Start with previously selected
        
        # Handle button clicks
        for i, day in enumerate(days_of_week):
            with day_cols[i]:
                is_selected = day in selected_workout_days
                button_type = "primary" if is_selected else "secondary"
                button_label = f"✅ {day}" if is_selected else day
                
                # Use a unique key for each button
                if st.button(button_label, key=f"day_btn_{day}", type=button_type, use_container_width=True):
                    # Toggle selection
                    if day in selected_workout_days:
                        selected_workout_days.remove(day)
                    else:
                        selected_workout_days.append(day)
                    # Update session state immediately
                    st.session_state["temp_custom_workout_data"]["workout_days"] = selected_workout_days
                    st.rerun()
        
        # Display selected days
        if selected_workout_days:
            st.success(f"✅ Selected: {', '.join(selected_workout_days)} ({len(selected_workout_days)} day(s))")
        else:
            st.warning("⚠️ Please select at least one day")
        
        st.markdown("---")
        
        # Rest of the form
        with st.form("custom_workout_step1"):
            # Workout duration
            duration_options = ["15-20 minutes", "30 minutes", "45 minutes", "60 minutes", "75 minutes", "90+ minutes"]
            duration_index = duration_options.index(temp_data.get('workout_duration', '45 minutes')) if temp_data.get('workout_duration') in duration_options else 2
            workout_duration = st.selectbox(
                "⏱️ How long do you want each workout session to be?",
                duration_options,
                index=duration_index,
                key="custom_step1_duration"
            )
            
            # Primary goal
            goal_options = [
                "Build muscle / Gain strength",
                "Lose weight / Burn fat",
                "Improve endurance / Cardio fitness",
                "General fitness / Stay active",
                "Improve sports performance",
                "Rehabilitation / Recovery",
                "Build power / Explosiveness",
                "Tone and define muscles"
            ]
            goal_index = goal_options.index(temp_data.get('primary_goal', 'General fitness / Stay active')) if temp_data.get('primary_goal') in goal_options else 3
            primary_goal = st.selectbox(
                "🎯 What's your primary fitness goal?",
                goal_options,
                index=goal_index,
                key="custom_step1_goal"
            )
            
            next_button = st.form_submit_button("➡️ Next", use_container_width=True)
            
            if next_button:
                # Get current selected days from session state
                current_selected_days = st.session_state["temp_custom_workout_data"].get('workout_days', [])
                # Validate that at least one day is selected
                if not current_selected_days:
                    st.error("❌ Please select at least one workout day")
                else:
                    st.session_state["temp_custom_workout_data"]["workout_days"] = current_selected_days
                    st.session_state["temp_custom_workout_data"]["workout_duration"] = workout_duration
                    st.session_state["temp_custom_workout_data"]["primary_goal"] = primary_goal
                    st.session_state["custom_workout_step"] = 2
                    st.rerun()
    
    # Step 2: Focus Areas & Style
    elif current_step == 2:
        st.markdown("### 💪 Step 2: Focus Areas & Workout Style")
        with st.form("custom_workout_step2"):
            temp_data = st.session_state["temp_custom_workout_data"]
            
            # Focus areas
            focus_options = [
                "Full Body",
                "Chest",
                "Back",
                "Shoulders",
                "Arms (Biceps & Triceps)",
                "Legs (Quads, Hamstrings, Glutes)",
                "Core / Abs",
                "Cardio / Endurance"
            ]
            default_focus = temp_data.get('focus_areas', ['Full Body'])
            focus_areas = st.multiselect(
                "💪 Which muscle groups do you want to focus on? (Select all that apply)",
                focus_options,
                default=default_focus,
                key="custom_step2_focus"
            )
            
            # Workout style preference
            style_options = [
                "High intensity / Fast-paced",
                "Moderate intensity / Balanced",
                "Low intensity / Steady pace",
                "Circuit training / Minimal rest",
                "Traditional sets with rest",
                "Supersets / Drop sets",
                "Time-based / AMRAP style"
            ]
            style_index = style_options.index(temp_data.get('workout_style', 'Moderate intensity / Balanced')) if temp_data.get('workout_style') in style_options else 1
            workout_style = st.selectbox(
                "🔥 What's your preferred workout style?",
                style_options,
                index=style_index,
                key="custom_step2_style"
            )
            
            col_back, col_next = st.columns(2)
            with col_back:
                back_button = st.form_submit_button("⬅️ Back", use_container_width=True)
            with col_next:
                next_button = st.form_submit_button("➡️ Next", use_container_width=True)
            
            if back_button:
                st.session_state["custom_workout_step"] = 1
                st.rerun()
            elif next_button:
                st.session_state["temp_custom_workout_data"]["focus_areas"] = focus_areas
                st.session_state["temp_custom_workout_data"]["workout_style"] = workout_style
                st.session_state["custom_workout_step"] = 3
                st.rerun()
    
    # Step 3: Equipment, Experience & Details
    elif current_step == 3:
        st.markdown("### 🏋️ Step 3: Equipment, Experience & Details")
        with st.form("custom_workout_step3"):
            temp_data = st.session_state["temp_custom_workout_data"]
            
            # Equipment preference
            equipment_options = [
                "Use all available equipment",
                "Prefer free weights (dumbbells, barbells)",
                "Prefer machines",
                "Bodyweight + minimal equipment",
                "Cardio equipment focus"
            ]
            equipment_index = equipment_options.index(temp_data.get('equipment_preference', 'Use all available equipment')) if temp_data.get('equipment_preference') in equipment_options else 0
            equipment_preference = st.selectbox(
                "🏋️ Equipment preference?",
                equipment_options,
                index=equipment_index,
                key="custom_step3_equipment"
            )
            
            # Experience level for this workout
            experience_options = [
                "Complete beginner",
                "Some experience",
                "Intermediate",
                "Advanced",
                "Expert"
            ]
            experience_index = experience_options.index(temp_data.get('workout_experience', 'Intermediate')) if temp_data.get('workout_experience') in experience_options else 2
            workout_experience = st.selectbox(
                "📚 What's your experience level for this specific workout?",
                experience_options,
                index=experience_index,
                key="custom_step3_experience"
            )
            
            # Any injuries or limitations
            limitations = st.text_area(
                "⚠️ Any injuries, limitations, or areas to avoid? (Optional)",
                value=temp_data.get('limitations', ''),
                placeholder="e.g., Lower back injury, avoid heavy squats, knee problems...",
                key="custom_step3_limitations"
            )
            
            # Additional preferences
            additional_prefs = st.text_area(
                "💭 Any additional preferences or specific requests? (Optional)",
                value=temp_data.get('additional_prefs', ''),
                placeholder="e.g., I prefer morning workouts, I want to focus on form, I like variety...",
                key="custom_step3_prefs"
            )
            
            col_back, col_generate = st.columns(2)
            with col_back:
                back_button = st.form_submit_button("⬅️ Back", use_container_width=True)
            with col_generate:
                generate_button = st.form_submit_button("✨ Generate Workout", use_container_width=True)
            
            if back_button:
                st.session_state["custom_workout_step"] = 2
                st.rerun()
            elif generate_button:
                # Save all data
                st.session_state["temp_custom_workout_data"]["equipment_preference"] = equipment_preference
                st.session_state["temp_custom_workout_data"]["workout_experience"] = workout_experience
                st.session_state["temp_custom_workout_data"]["limitations"] = limitations
                st.session_state["temp_custom_workout_data"]["additional_prefs"] = additional_prefs
                
                # Get all collected data
                all_data = st.session_state["temp_custom_workout_data"]
                
                # Build comprehensive workout request
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                lifestyle = user_data.get("lifestyle", "Student or office worker")
                exercise_experience = user_data.get("exercise_experience", "Beginner")
                height_cm = user_data.get("height_cm", 175)
                weight_kg = user_data.get("weight_kg", 70)
                weight_lbs = user_data.get("weight_lbs", round(weight_kg * 2.20462, 1))
                
                focus_str = ", ".join(all_data.get('focus_areas', ['Full Body'])) if all_data.get('focus_areas') else "Full Body"
                limitations_str = f"\n\nIMPORTANT LIMITATIONS TO CONSIDER: {all_data.get('limitations', '')}" if all_data.get('limitations') else ""
                prefs_str = f"\n\nADDITIONAL PREFERENCES: {all_data.get('additional_prefs', '')}" if all_data.get('additional_prefs') else ""
                
                # Format workout days
                workout_days = all_data.get('workout_days', [])
                workout_days_str = ", ".join(workout_days) if workout_days else "Not specified"
                num_days = len(workout_days)
                
                custom_prompt = f"""Create a completely personalized and custom workout routine specifically designed for me based on ALL the following information:

MY PROFILE:
- Age: {age} years old
- Gender: {gender}
- Height: {height_cm}cm ({int(height_cm/30.48)}ft {int((height_cm%30.48)/2.54)}in)
- Weight: {weight_kg}kg ({weight_lbs}lbs)
- Current fitness level: {fitness_level}
- Exercise experience: {exercise_experience}
- Lifestyle: {lifestyle}
- Current exercise frequency: {exercise_frequency}
- Sports/Activities: {', '.join(sports_activities) if sports_activities else 'None'}

MY WORKOUT PREFERENCES:
- Desired workout days: {workout_days_str} ({num_days} day(s) per week)
- Desired workout duration: {all_data.get('workout_duration')}
- Primary fitness goal: {all_data.get('primary_goal')}
- Focus areas: {focus_str}
- Preferred workout style: {all_data.get('workout_style')}
- Equipment preference: {all_data.get('equipment_preference')}
- Experience level for this workout: {all_data.get('workout_experience')}{limitations_str}{prefs_str}

Please create a detailed, personalized workout plan using the available gym equipment that:
1. Is scheduled for these specific days: {workout_days_str} ({num_days} day(s) per week)
2. Matches my desired duration: {all_data.get('workout_duration')}
3. Aligns with my primary goal: {all_data.get('primary_goal')}
4. Focuses on: {focus_str}
5. Uses my preferred style: {all_data.get('workout_style')}
6. Respects my equipment preference: {all_data.get('equipment_preference')}
7. Is appropriate for my experience level: {all_data.get('workout_experience')}
8. Includes specific exercises, sets, reps, rest periods, and progression
9. Considers all my profile information and preferences
10. Provides proper warm-up and cool-down
11. Is safe, effective, and tailored specifically for me

Make it the perfect workout routine for my needs!"""
                
                # Store the actual prompt but show a friendly message
                st.session_state["pre_filled_question"] = custom_prompt
                st.session_state["custom_workout_request"] = True  # Flag to show friendly message
                
                # Reset custom workout form state
                st.session_state["custom_workout_step"] = 1
                st.session_state["temp_custom_workout_data"] = {}
                
                st.success("✅ Custom workout request generated!")
                st.info("🔄 Redirecting to main app...")
                
                # Redirect to main app
                st.switch_page("pages/3_main_app.py")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Back to main app button
st.markdown("---")
if st.button("🔙 Back to Main App", use_container_width=True):
    # Reset form state
    st.session_state["custom_workout_step"] = 1
    st.session_state["temp_custom_workout_data"] = {}
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

