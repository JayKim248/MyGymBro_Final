# 💪 MyGymBro - Student Gym Routine Builder

## 🚀 Quick Start

```bash
# Navigate to the personal_Project directory
cd personal_Project

# Install dependencies (if using pip)
pip install streamlit langchain langchain-openai langchain-teddynote python-dotenv

# Set up environment variables
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Run the application
streamlit run main.py
```

## 🎯 Features

### AI Routine Builder Modes
- **기본모드**: General student gym routine assistant
- **초보자 루틴**: Beginner-friendly routines with step-by-step guidance
- **시간별 루틴**: Time-efficient routines (30min, 45min, 60min)
- **부위별 루틴**: Targeted routines for specific muscle groups
- **기구 사용법**: Equipment usage guides and safety tips
- **학생 동기부여**: Student-specific motivation and encouragement
- **SNS 게시글**: Student fitness content for social media

### Student-Focused Tools
- **BMI Calculator**: Track your health metrics
- **루틴 세트 계산기**: Calculate workout sets and repetitions
- **학생 프로필 관리**: Save your fitness level and available time

### UI Features
- Modern, student-friendly gradient design
- Responsive layout with sidebar tools
- Real-time chat interface
- Error handling and user feedback

## 🛠️ Preserved Functions

All original functions from your codebase are preserved:
- `create_chain()` - Enhanced with student gym routine prompts
- `print_message()` - Chat message display
- `add_message()` - Session state management
- `weird()` - Mathematical utility function
- User profile management functions

## 🎨 Student-Focused Design

The application is specifically designed for students with:
- Student-friendly color scheme and gradients
- Academic and fitness themed UI elements
- Specialized AI prompts for student gym routines
- Time-conscious workout planning
- Student motivation and encouragement

## 📝 Environment Setup

Create a `.env` file in the `personal_Project` directory:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

## 🏃‍♂️ Usage

1. Select your preferred routine builder mode from the sidebar
2. Use the BMI calculator to track your health metrics
3. Save your student profile with your fitness level and available time
4. Chat with the AI to build personalized gym routines
5. Get beginner-friendly guidance, time-efficient workouts, and student motivation!

## 🎓 Student Benefits

- **Time-efficient routines** that fit busy student schedules
- **Beginner-friendly guidance** for those new to the gym
- **Equipment tutorials** to build confidence
- **Student-specific motivation** during exam periods and stress
- **Flexible scheduling** based on your available time

---

**MyGymBro** - Your AI Gym Buddy for Student Success! 💪🎓
