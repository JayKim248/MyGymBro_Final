"""
MyGymBro - Student Gym Routine Builder
Main Application Page

=== 주요 변경 사항 (Major Changes) ===
	
1. 오토스크롤 문제 해결 (Auto-scroll Issue Resolution)
   - 문제: JavaScript 기반 scroll 기능이 충돌을 일으키고 메시지 표시에 문제 발생
   - 해결: 모든 JavaScript scroll 코드 제거하고 Streamlit의 기본 rerun() 메커니즘만 사용
   - 동작 방식:
     * 사용자 입력/버튼 클릭 → session_state에 메시지 추가 → st.rerun()
     * rerun 후 모든 메시지를 for loop로 다시 표시
     * Streamlit이 자동으로 새 메시지가 추가될 때 하단으로 스크롤 처리

2. 메시지 처리 구조 개선 (Message Handling Structure Improvement)
   - 이전: 메시지를 화면에 먼저 표시 → session_state에 저장
   - 변경: 메시지를 session_state에 먼저 저장 → rerun → 모든 메시지 다시 표시
   - 참고: 09-MiniProject-seungri/pages/3_main_chat.py 구조 적용
   - 장점: 메시지 중복 방지, 일관된 상태 관리, 자연스러운 스크롤

3. UI 레이아웃 재구성 (UI Layout Restructuring)
   - 버튼 메뉴를 메인 영역에서 사이드바로 이동
   - 사이드바에 expander를 사용하여 카테고리별로 정리:
     * 💪 Basic Workouts (기본 열림)
     * 🎯 Advanced Workouts (기본 닫힘)
     * 😂 Fun & Meme Workouts (기본 닫힘)
     * 👑 Clash Royale Themed (특정 사용자용, 기본 닫힘)
     * 📊 Additional Tools
   - 메인 영역: 채팅 인터페이스만 표시 (깔끔한 대화 중심 UI)

4. 코드 단순화 (Code Simplification)
   - try-except 블록 제거: 에러 처리를 Streamlit 기본 방식으로 변경
   - Loading spinner 제거: 사용자 메시지가 먼저 표시되고, 그 다음 AI 응답 생성
   - 2단계 처리 방식:
     * 1단계: 사용자 입력 → session_state에 추가 → rerun (사용자 메시지 표시)
     * 2단계: 마지막 메시지가 user인지 확인 → AI 응답 생성 → session_state에 추가 → rerun (AI 응답 표시)

5. Pre-filled Question 처리 개선
   - 버튼 클릭 시 pre_filled_question 설정 → 즉시 rerun
   - rerun 후 pre_filled_question 처리 → 사용자 메시지로 변환 → 다시 rerun
   - elif를 사용하여 chat_input과 분리하여 충돌 방지

=== 기술적 세부사항 (Technical Details) ===

- Scroll 관련 제거된 코드:
  * JavaScript scrollToBottom(), scrollToChatInput() 함수
  * window.addEventListener('load', scrollToBottom)
  * window.addEventListener('message', ...) 이벤트 리스너
  * setTimeout을 사용한 scroll 호출

- 메시지 표시 방식:
  * for message in st.session_state["messages"]: st.chat_message(...).write(...)
  * rerun할 때마다 전체 메시지 리스트를 다시 렌더링
  * Streamlit이 자동으로 새 콘텐츠에 맞춰 스크롤 조정

- 상태 관리:
  * session_state["messages"]: 모든 대화 메시지 저장
  * session_state["pre_filled_question"]: 버튼 클릭 시 생성되는 질문
  * session_state["prefilled_triggered"]: pre-filled question 플래그
"""

import streamlit as st
from dotenv import load_dotenv
import json
from pathlib import Path
import os
from openai import OpenAI
import pandas as pd
import re

# Try to import matplotlib, but make it optional
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Environment mode: default prod so .env is always loaded unless explicitly set to local
APP_ENV = os.getenv("APP_ENV", "prod").lower()

# Always load .env (publishing/default). Local can still override via APP_ENV=local.
load_dotenv(".env")

# Page configuration
st.set_page_config(
    page_title="MyGymBro - Student Gym Routine Builder",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .fitness-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
    }
    .stChatMessage {
        margin-bottom: 1rem;
    }
    .workout-block {
        background: white;
        border: 2px solid #4ecdc4;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .workout-block:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    .workout-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}
# Custom workout form state
if "custom_workout_step" not in st.session_state:
    st.session_state["custom_workout_step"] = 1
if "temp_custom_workout_data" not in st.session_state:
    st.session_state["temp_custom_workout_data"] = {}
# Removed scroll tracking variables - using simpler approach

# Data directory setup
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USER_PROFILE_PATH = DATA_DIR / "user_profiles.json"
USERS_FILE = DATA_DIR / "users.json"
EQUIPMENT_FILE = DATA_DIR / "GymMachineList.xlsx"

# Functions to load and save user data
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
    """Update user profile data in the JSON file and session state."""
    users = load_users()
    if email in users:
        # Update the user data
        users[email].update(updated_data)
        save_users(users)
        
        # Update session state
        st.session_state["user_data"] = users[email]
        return True
    return False

# Translation dictionaries
TRANSLATIONS = {
    "English": {
        "app_title": "MyGymBro - Student Gym Routine Builder",
        "welcome": "Welcome to MyGymBro! 💪",
        "subtitle": "Your AI-powered gym routine builder for students",
        "calorie_calculator": "Calorie Calculator",
        "gender": "Gender",
        "age": "Age",
        "height": "Height",
        "weight": "Weight (lbs)",
        "lifestyle": "Lifestyle",
        "exercise_experience": "Exercise Experience",
        "exercise_frequency": "Exercise Frequency",
        "fitness_level": "Fitness Level",
        "sports": "Sports/Activities",
        "calculate_calories": "Calculate Calories",
        "maintenance_calories": "Maintenance Calories",
        "bmr": "BMR (Basal Metabolic Rate)",
        "activity_metabolism": "Activity Metabolism",
        "total_metabolism": "Total Metabolism",
        "daily_intake": "Daily Recommended Intake",
        "weight_loss": "Weight Loss",
        "weight_maintenance": "Weight Maintenance",
        "bulk_up": "Bulk Up",
        "target_calories": "Target Calories",
        "macros": "Macronutrients",
        "carbs": "Carbohydrates",
        "protein": "Protein",
        "fat": "Fat",
        "cardio_intensity": "Recommended Cardio Intensity",
        "heart_rate_range": "Heart Rate Range",
        "bpm": "bpm",
        "chat_title": "💬 Chat with MyGymBro",
        "chat_placeholder": "💬 Ask follow-up questions or request more details!",
        "loading_message": "🤖 MyGymBro is preparing an answer...",
        "error_message": "Hello! I'm MyGymBro. Currently there's a network connection issue and I can't provide AI responses. Please try again later. In the meantime, try using the BMI calculator or routine set calculator!",
        "footer": "💪 MyGymBro - Student Gym Routine Builder | Powered by OpenAI",
        "footer_subtitle": "Perfect gym routines for students, start with MyGymBro!",
        "language": "Language",
        "select_language": "Select Language"
    },
    "French": {
        "app_title": "MyGymBro - Créateur de Routine de Gym pour Étudiants",
        "welcome": "Bienvenue chez MyGymBro! 💪",
        "subtitle": "Votre créateur de routine de gym alimenté par l'IA pour étudiants",
        "calorie_calculator": "Calculateur de Calories",
        "gender": "Sexe",
        "age": "Âge",
        "height": "Taille",
        "weight": "Poids (lbs)",
        "lifestyle": "Mode de Vie",
        "exercise_experience": "Expérience d'Exercice",
        "exercise_frequency": "Fréquence d'Exercice",
        "fitness_level": "Niveau de Forme",
        "sports": "Sports/Activités",
        "calculate_calories": "Calculer les Calories",
        "maintenance_calories": "Calories de Maintien",
        "bmr": "BMR (Métabolisme de Base)",
        "activity_metabolism": "Métabolisme d'Activité",
        "total_metabolism": "Métabolisme Total",
        "daily_intake": "Apport Quotidien Recommandé",
        "weight_loss": "Perte de Poids",
        "weight_maintenance": "Maintien du Poids",
        "bulk_up": "Prise de Masse",
        "target_calories": "Calories Cibles",
        "macros": "Macronutriments",
        "carbs": "Glucides",
        "protein": "Protéines",
        "fat": "Lipides",
        "cardio_intensity": "Intensité Cardio Recommandée",
        "heart_rate_range": "Plage de Fréquence Cardiaque",
        "bpm": "bpm",
        "chat_title": "💬 Discutez avec MyGymBro",
        "chat_placeholder": "💬 Posez des questions de suivi ou demandez plus de détails!",
        "loading_message": "🤖 MyGymBro prépare une réponse...",
        "error_message": "Bonjour! Je suis MyGymBro. Actuellement il y a un problème de connexion réseau et je ne peux pas fournir de réponses IA. Veuillez réessayer plus tard. En attendant, essayez le calculateur de série de routine!",
        "footer": "💪 MyGymBro - Créateur de Routine de Gym pour Étudiants | Alimenté par OpenAI",
        "footer_subtitle": "Routines de gym parfaites pour étudiants, commencez avec MyGymBro!",
        "language": "Langue",
        "select_language": "Sélectionner la Langue"
    },
    "Korean": {
        "app_title": "MyGymBro - 학생용 짐 루틴 빌더",
        "welcome": "MyGymBro에 오신 것을 환영합니다! 💪",
        "subtitle": "학생들을 위한 AI 기반 짐 루틴 빌더",
        "calorie_calculator": "칼로리 계산기",
        "gender": "성별",
        "age": "나이",
        "height": "키",
        "weight": "몸무게 (lbs)",
        "lifestyle": "생활습관",
        "exercise_experience": "운동 경력",
        "exercise_frequency": "운동 횟수",
        "fitness_level": "체력수준",
        "sports": "운동/활동",
        "calculate_calories": "칼로리 계산",
        "maintenance_calories": "유지 칼로리",
        "bmr": "기초대사량",
        "activity_metabolism": "활동 대사량",
        "total_metabolism": "총 대사량",
        "daily_intake": "하루 권장 섭취량",
        "weight_loss": "체중 감소",
        "weight_maintenance": "체중 유지",
        "bulk_up": "벌크업",
        "target_calories": "목표 섭취 칼로리",
        "macros": "탄단지 매크로",
        "carbs": "탄수화물",
        "protein": "단백질",
        "fat": "지방",
        "cardio_intensity": "권장 유산소 강도",
        "heart_rate_range": "추천 심박수 범위",
        "bpm": "bpm",
        "chat_title": "💬 MyGymBro와 대화하기",
        "chat_placeholder": "💬 추가 질문이나 더 자세한 정보를 요청하세요!",
        "loading_message": "🤖 MyGymBro가 답변을 준비하고 있습니다...",
        "error_message": "안녕하세요! MyGymBro입니다. 현재 네트워크 연결에 문제가 있어 AI 응답을 받을 수 없습니다. 잠시 후 다시 시도해주세요. 그동안 루틴 세트 계산기를 사용해보세요!",
        "footer": "💪 MyGymBro - Student Gym Routine Builder | Powered by OpenAI",
        "footer_subtitle": "학생들을 위한 완벽한 짐 루틴, MyGymBro와 함께 시작하세요!",
        "language": "언어",
        "select_language": "언어 선택"
    },
    "Mandarin": {
        "app_title": "MyGymBro - 学生健身计划构建器",
        "welcome": "欢迎使用MyGymBro！💪",
        "subtitle": "您的AI驱动学生健身计划构建器",
        "calorie_calculator": "卡路里计算器",
        "gender": "性别",
        "age": "年龄",
        "height": "身高",
        "weight": "体重（磅）",
        "lifestyle": "生活方式",
        "exercise_experience": "运动经验",
        "exercise_frequency": "运动频率",
        "fitness_level": "健身水平",
        "sports": "运动/活动",
        "calculate_calories": "计算卡路里",
        "maintenance_calories": "维持卡路里",
        "bmr": "基础代谢率",
        "activity_metabolism": "活动代谢",
        "total_metabolism": "总代谢",
        "daily_intake": "每日推荐摄入量",
        "weight_loss": "减重",
        "weight_maintenance": "维持体重",
        "bulk_up": "增肌",
        "target_calories": "目标卡路里",
        "macros": "宏量营养素",
        "carbs": "碳水化合物",
        "protein": "蛋白质",
        "fat": "脂肪",
        "cardio_intensity": "推荐有氧强度",
        "heart_rate_range": "推荐心率范围",
        "bpm": "bpm",
        "chat_title": "💬 与MyGymBro聊天",
        "chat_placeholder": "💬 提出后续问题或请求更多详细信息！",
        "loading_message": "🤖 MyGymBro正在准备答案...",
        "error_message": "你好！我是MyGymBro。目前网络连接有问题，无法提供AI回复。请稍后再试。同时，可以试试计划组计算器！",
        "footer": "💪 MyGymBro - 学生健身计划构建器 | 由OpenAI驱动",
        "footer_subtitle": "学生的完美健身计划，与MyGymBro一起开始！",
        "language": "语言",
        "select_language": "选择语言"
    },
    "Spanish": {
        "app_title": "MyGymBro - Constructor de Rutinas de Gimnasio para Estudiantes",
        "welcome": "¡Bienvenido a MyGymBro! 💪",
        "subtitle": "Tu constructor de rutinas de gimnasio con IA para estudiantes",
        "calorie_calculator": "Calculadora de Calorías",
        "gender": "Género",
        "age": "Edad",
        "height": "Altura",
        "weight": "Peso (lbs)",
        "lifestyle": "Estilo de Vida",
        "exercise_experience": "Experiencia de Ejercicio",
        "exercise_frequency": "Frecuencia de Ejercicio",
        "fitness_level": "Nivel de Fitness",
        "sports": "Deportes/Actividades",
        "calculate_calories": "Calcular Calorías",
        "maintenance_calories": "Calorías de Mantenimiento",
        "bmr": "TMB (Tasa Metabólica Basal)",
        "activity_metabolism": "Metabolismo de Actividad",
        "total_metabolism": "Metabolismo Total",
        "daily_intake": "Ingesta Diaria Recomendada",
        "weight_loss": "Pérdida de Peso",
        "weight_maintenance": "Mantenimiento de Peso",
        "bulk_up": "Aumento de Masa",
        "target_calories": "Calorías Objetivo",
        "macros": "Macronutrientes",
        "carbs": "Carbohidratos",
        "protein": "Proteína",
        "fat": "Grasa",
        "cardio_intensity": "Intensidad Cardio Recomendada",
        "heart_rate_range": "Rango de Frecuencia Cardíaca",
        "bpm": "lpm",
        "chat_title": "💬 Chatea con MyGymBro",
        "chat_placeholder": "💬 ¡Haz preguntas de seguimiento o solicita más detalles!",
        "loading_message": "🤖 MyGymBro está preparando una respuesta...",
        "error_message": "¡Hola! Soy MyGymBro. Actualmente hay un problema de conexión de red y no puedo proporcionar respuestas de IA. Por favor, inténtalo de nuevo más tarde. Mientras tanto, ¡prueba la calculadora de series de rutina!",
        "footer": "💪 MyGymBro - Constructor de Rutinas de Gimnasio para Estudiantes | Impulsado por OpenAI",
        "footer_subtitle": "¡Rutinas de gimnasio perfectas para estudiantes, comienza con MyGymBro!",
        "language": "Idioma",
        "select_language": "Seleccionar Idioma"
    }
}

def get_text(key):
    """Get translated text based on current language."""
    return TRANSLATIONS[st.session_state["language"]].get(key, key)

def logout_user():
    """Logout user and clear session state."""
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = None
    st.session_state["user_data"] = {}
    st.session_state["messages"] = []
    st.rerun()

def check_authentication():
    """Check if user is authenticated, redirect to login if not."""
    if not st.session_state.get("authenticated", False):
        st.warning("🔐 Please log in to access MyGymBro")
        if st.button("Go to Login", use_container_width=True):
            st.switch_page("pages/1_login.py")
        st.stop()


# Load gym equipment data
def load_gym_equipment():
    """Load gym equipment data from Excel file."""
    try:
        if EQUIPMENT_FILE.exists():
            df = pd.read_excel(EQUIPMENT_FILE)
            return df
        else:
            # Create a sample equipment list if file doesn't exist
            sample_equipment = {
                'Equipment': ['Bench Press', 'Squat Rack', 'Dumbbells', 'Barbells', 'Treadmill', 'Rowing Machine'],
                'Quantity': [2, 1, 10, 4, 3, 2],
                'Location': ['Main Area', 'Main Area', 'Free Weights', 'Free Weights', 'Cardio Zone', 'Cardio Zone'],
                'Status': ['Available', 'Available', 'Available', 'Available', 'Available', 'Available']
            }
            df = pd.DataFrame(sample_equipment)
            df.to_excel(EQUIPMENT_FILE, index=False)
            return df
    except Exception as e:
        st.error(f"Error loading equipment data: {str(e)}")
        return None

def get_equipment_summary():
    """Get a summary of available equipment for AI prompts."""
    df = load_gym_equipment()
    if df is not None:
        equipment_list = []
        for _, row in df.iterrows():
            # Handle different column structures
            machine_name = row.get('Machine', row.get('Equipment', 'Unknown'))
            quantity = row.get('Quantity', 'N/A')
            min_weight = row.get('Min_Weights(lbs)', 'N/A')
            max_weight = row.get('Max_weights(lbs)', 'N/A')
            
            # Create detailed equipment info
            weight_info = f" ({min_weight}-{max_weight} lbs)" if min_weight != 'N/A' and max_weight != 'N/A' else ""
            equipment_list.append(f"- {machine_name} (Qty: {quantity}{weight_info})")
        return "\n".join(equipment_list)
    return "Equipment data not available"


# Calorie calculation functions
def calculate_bmr(gender, age, height, weight):
    """Calculate Basal Metabolic Rate using Harris-Benedict equation."""
    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:  # Female
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return round(bmr, 1)

def calculate_activity_multiplier(lifestyle, exercise_frequency, fitness_level):
    """Calculate activity multiplier based on lifestyle and exercise habits."""
    base_multipliers = {
        "Lying down 15+ hours": 1.0,
        "Almost no movement at home": 1.1,
        "Student or office worker": 1.2,
        "Active": 1.3,
        "Very active": 1.4
    }
    
    exercise_bonus = {
        "None": 0,
        "1x/week": 0.05,
        "2x/week": 0.1,
        "3x/week": 0.15,
        "4x/week": 0.2,
        "5x/week": 0.25,
        "6x/week": 0.3,
        "7x/week": 0.35
    }
    
    fitness_bonus = {
        "Very poor": 0,
        "Poor": 0.02,
        "Below average": 0.05,
        "Average": 0.08,
        "Above average": 0.12,
        "Good": 0.15,
        "Very good": 0.2
    }
    
    base = base_multipliers.get(lifestyle, 1.2)
    exercise = exercise_bonus.get(exercise_frequency, 0)
    fitness = fitness_bonus.get(fitness_level, 0)
    
    return base + exercise + fitness

def calculate_macros(calories, goal="maintenance"):
    """Calculate macronutrient distribution."""
    if goal == "weight_loss":
        calories = calories - 500
    elif goal == "bulk_up":
        calories = calories + 500
    
    # 5:3:2 ratio (carbs:protein:fat)
    protein_calories = calories * 0.3
    carb_calories = calories * 0.5
    fat_calories = calories * 0.2
    
    protein_grams = round(protein_calories / 4, 1)
    carb_grams = round(carb_calories / 4, 1)
    fat_grams = round(fat_calories / 9, 1)
    
    return {
        "calories": calories,
        "protein": protein_grams,
        "carbs": carb_grams,
        "fat": fat_grams
    }

def calculate_heart_rate_range(age, fitness_level):
    """Calculate recommended heart rate range for fat burning."""
    max_hr = 220 - age
    
    # MFO (Maximal Fat Oxidation) zones based on fitness level
    zones = {
        "Very poor": (0.5, 0.6),
        "Poor": (0.55, 0.65),
        "Below average": (0.6, 0.7),
        "Average": (0.65, 0.75),
        "Above average": (0.7, 0.8),
        "Good": (0.75, 0.85),
        "Very good": (0.8, 0.9)
    }
    
    min_zone, max_zone = zones.get(fitness_level, (0.65, 0.75))
    min_hr = int(max_hr * min_zone)
    max_hr = int(max_hr * max_zone)
    
    return min_hr, max_hr

def calculate_body_fat_navy(gender, age, height_cm, weight_kg, waist_cm, neck_cm=None):
    """
    Calculate body fat percentage using Navy Method.
    Requires: gender, age, height, weight, waist circumference
    Optional: neck circumference (for more accurate calculation)
    """
    # Convert cm to inches for Navy formula
    height_inches = height_cm / 2.54
    waist_inches = waist_cm / 2.54
    neck_inches = neck_cm / 2.54 if neck_cm else None
    
    if gender.lower() in ["male", "m"]:
        # Navy method for men
        if neck_inches:
            body_fat = 86.010 * ((waist_inches - neck_inches) / height_inches) - 70.041
        else:
            # Simplified version without neck measurement
            # Using waist-to-height ratio
            body_fat = 64 - (20 * (height_inches / waist_inches)) + (12 * age / 100)
    else:
        # Navy method for women (requires additional hip measurement)
        # Using simplified BMI-based method for women
        bmi = weight_kg / ((height_cm / 100) ** 2)
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    
    return max(5, min(50, round(body_fat, 1)))  # Clamp between 5% and 50%

def calculate_body_fat_bmi(gender, age, height_cm, weight_kg):
    """
    Calculate body fat percentage using Deurenberg formula (BMI-based).
    Simpler method that doesn't require body measurements.
    """
    bmi = weight_kg / ((height_cm / 100) ** 2)
    
    if gender.lower() in ["male", "m"]:
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    
    return max(5, min(50, round(body_fat, 1)))  # Clamp between 5% and 50%

def get_body_fat_category(body_fat, gender):
    """Get body fat category based on percentage."""
    if gender.lower() in ["male", "m"]:
        categories = {
            (0, 6): ("Essential Fat", "#4CAF50"),
            (6, 14): ("Athletes", "#8BC34A"),
            (14, 18): ("Fitness", "#CDDC39"),
            (18, 25): ("Average", "#FFC107"),
            (25, 32): ("Obese", "#FF9800"),
            (32, 100): ("Very High", "#F44336")
        }
    else:
        categories = {
            (0, 14): ("Essential Fat", "#4CAF50"),
            (14, 21): ("Athletes", "#8BC34A"),
            (21, 25): ("Fitness", "#CDDC39"),
            (25, 32): ("Average", "#FFC107"),
            (32, 38): ("Obese", "#FF9800"),
            (38, 100): ("Very High", "#F44336")
        }
    
    for (low, high), (category, color) in categories.items():
        if low <= body_fat < high:
            return category, color
    return "Unknown", "#9E9E9E"

def parse_workout_exercises(text):
    """Parse workout text to extract individual exercises."""
    exercises = []
    lines = text.split('\n')
    current_exercise = None
    current_description = []
    
    # Patterns to match exercise numbers (1., 2., First, Second, etc.)
    exercise_patterns = [
        r'^\d+[\.\)]\s*(.+?)(?:\s*[-–—]|$)',  # 1. Exercise Name or 1) Exercise Name
        r'^(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s*[:\-]?\s*(.+?)(?:\s*[-–—]|$)',  # First: Exercise Name
        r'^Exercise\s+\d+[:\-]?\s*(.+?)(?:\s*[-–—]|$)',  # Exercise 1: Exercise Name
    ]
    
    # Skip intro sections (warm-up, introduction, etc.)
    skip_sections = ['warm-up', 'warmup', 'introduction', 'overview', 'summary', 'cool-down', 'cooldown']
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            # Empty line might separate exercises
            if current_exercise and current_description:
                # Don't add empty line, but continue collecting
                continue
            continue
        
        # Skip section headers
        line_lower = line.lower()
        if any(section in line_lower for section in skip_sections) and len(line) < 50:
            # Reset current exercise if we hit a section header
            if current_exercise:
                exercises.append({
                    'name': current_exercise,
                    'description': '\n'.join(current_description).strip()
                })
                current_exercise = None
                current_description = []
            continue
        
        # Check if this line starts a new exercise
        is_exercise_start = False
        exercise_name = None
        
        for pattern in exercise_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                exercise_name = match.group(1).strip()
                # Clean up exercise name (remove extra punctuation)
                exercise_name = re.sub(r'^[-–—\s]+|[-–—\s]+$', '', exercise_name)
                if exercise_name:
                    is_exercise_start = True
                    break
        
        # Also check for bold text (markdown format)
        if not is_exercise_start:
            bold_match = re.match(r'^\*\*(.+?)\*\*', line)
            if bold_match:
                potential_name = bold_match.group(1).strip()
                # Check if it looks like an exercise name (not too long, not a full sentence)
                if len(potential_name) < 80 and ':' not in potential_name:
                    exercise_name = potential_name
                    is_exercise_start = True
        
        # Check for lines that start with common exercise patterns
        if not is_exercise_start:
            # Look for lines that might be exercise names (short, capitalized, contain exercise keywords)
            exercise_keywords = ['squat', 'press', 'curl', 'row', 'pull', 'push', 'deadlift', 'lunge', 'plank', 'crunch', 'bench', 'fly', 'extension', 'raise', 'dip']
            if len(line) < 80 and any(keyword in line_lower for keyword in exercise_keywords):
                # Check if it's likely an exercise name (starts with capital, short, no colon in middle)
                if line[0].isupper() and line.count(':') <= 1:
                    parts = line.split(':', 1)
                    if len(parts) == 1 or (len(parts) == 2 and len(parts[0]) < 60):
                        exercise_name = parts[0].strip()
                        is_exercise_start = True
        
        if is_exercise_start and exercise_name:
            # Save previous exercise if exists
            if current_exercise:
                exercises.append({
                    'name': current_exercise,
                    'description': '\n'.join(current_description).strip()
                })
            
            # Start new exercise
            current_exercise = exercise_name
            current_description = []
            # Add the rest of the line as description if it contains more info
            if ':' in line:
                remaining = line.split(':', 1)[1].strip()
                if remaining:
                    current_description.append(remaining)
        else:
            # Add to current exercise description
            if current_exercise:
                # Skip if this looks like the start of a new section
                if not (line_lower.startswith('workout') or line_lower.startswith('day') or 
                        any(section in line_lower for section in skip_sections)):
                    current_description.append(line)
            elif not exercises:  # If no exercise found yet, might be intro text
                pass
    
    # Add last exercise
    if current_exercise:
        exercises.append({
            'name': current_exercise,
            'description': '\n'.join(current_description).strip()
        })
    
    # If no exercises found with patterns, try alternative parsing
    if not exercises:
        # Look for numbered list items
        for i, line in enumerate(lines):
            line = line.strip()
            if re.match(r'^\d+[\.\)]\s+', line):
                # Extract exercise name
                exercise_name = re.sub(r'^\d+[\.\)]\s+', '', line).strip()
                # Get description from next few lines
                desc_lines = []
                for j in range(i+1, min(i+6, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not re.match(r'^\d+[\.\)]\s+', next_line):
                        desc_lines.append(next_line)
                    else:
                        break
                if exercise_name:
                    exercises.append({
                        'name': exercise_name,
                        'description': '\n'.join(desc_lines).strip()
                    })
    
    # Filter out exercises with very short or invalid names
    exercises = [ex for ex in exercises if ex['name'] and len(ex['name']) > 2]
    
    return exercises

def display_workout_blocks(response_text):
    """Display workout in block/spreadsheet style with clickable buttons."""
    exercises = parse_workout_exercises(response_text)
    
    if not exercises:
        # If parsing failed, display as regular text
        return False
    
    # Display workout blocks
    st.markdown("### 💪 Your Workout Plan")
    st.markdown("*Click on each workout block to see detailed instructions*")
    st.markdown("---")
    
    # Create a grid layout for workout blocks
    num_exercises = len(exercises)
    cols_per_row = 3
    
    for i in range(0, num_exercises, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < num_exercises:
                exercise = exercises[i + j]
                exercise_num = i + j + 1
                
                with col:
                    # Create workout block button
                    ordinal = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"][exercise_num - 1] if exercise_num <= 10 else f"{exercise_num}th"
                    
                    # Truncate exercise name for display
                    display_name = exercise['name'][:35] + "..." if len(exercise['name']) > 35 else exercise['name']
                    
                    # Use expander for each workout block
                    with st.expander(f"🏋️ {ordinal} Workout: {display_name}", expanded=False):
                        st.markdown(f"### {exercise['name']}")
                        st.markdown("---")
                        
                        # Try to extract sets/reps, form tips, etc. from description
                        desc_text = exercise['description'].lower() if exercise['description'] else ""
                        
                        # Look for sets/reps pattern
                        sets_reps_match = re.search(r'(\d+)\s*(?:sets?|x)\s*(?:of\s*)?(\d+)', desc_text)
                        if sets_reps_match:
                            st.markdown(f"**📊 Sets/Reps:** {sets_reps_match.group(1)} sets x {sets_reps_match.group(2)} reps")
                        
                        # Look for rest period
                        rest_match = re.search(r'rest[:\s]+(\d+[-\s]?\d*)\s*(?:seconds?|sec|minutes?|min)', desc_text)
                        if rest_match:
                            st.markdown(f"**⏱️ Rest:** {rest_match.group(1)}")
                        
                        # Look for weight information
                        weight_match = re.search(r'(\d+[-\s]?\d*)\s*(?:lbs?|kg|pounds?|kilograms?)', desc_text)
                        if weight_match:
                            st.markdown(f"**🏋️ Weight:** {weight_match.group(1)}")
                        
                        # Display description
                        if exercise['description']:
                            st.markdown("---")
                            st.markdown("#### 📝 Description & Instructions")
                            st.markdown(exercise['description'])
                            
                            # Try to extract form tips
                            form_keywords = ['form', 'technique', 'posture', 'position', 'keep', 'maintain', 'avoid']
                            if any(keyword in desc_text for keyword in form_keywords):
                                st.markdown("---")
                                st.markdown("#### ✅ Proper Form Tips")
                                # Extract sentences with form-related keywords
                                sentences = exercise['description'].split('.')
                                form_sentences = [s.strip() + '.' for s in sentences if any(keyword in s.lower() for keyword in form_keywords)]
                                if form_sentences:
                                    for tip in form_sentences[:3]:  # Show up to 3 form tips
                                        st.markdown(f"• {tip}")
    
    return True

# AI response function - returns a generator for streaming
def get_ai_response_stream(question, prompt_type):
    import ssl
    import httpx
    
    # Choose API key source based on environment
    if APP_ENV == "local":
        # Local: use OPENAI_API_KEY_LOCAL if provided, else fallback to OPENAI_API_KEY
        api_key = os.environ.get('OPENAI_API_KEY_LOCAL') or os.environ.get('OPENAI_API_KEY')
    else:
        # Default/prod: use OPENAI_API_KEY from .env (loaded above)
        api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        error_msg = (
            "⚠️ **OpenAI API Key Not Configured**\n\n"
            "To use MyGymBro's AI features, you need to set up your OpenAI API key:\n\n"
            "**Option 1: Create a .env file**\n"
            "1. Create a file named `.env` in the project root\n"
            "2. Add this line: `OPENAI_API_KEY=your_actual_api_key_here`\n"
            "3. Get your API key from: https://platform.openai.com/api-keys\n\n"
            "**Option 2: Set environment variable**\n"
            "Run: `export OPENAI_API_KEY=your_actual_api_key_here`\n\n"
            "After setting up, restart the Streamlit app."
        )
        yield error_msg
        return
    
    # Strip whitespace from API key
    api_key = api_key.strip()
    
    # Create client with SSL verification disabled for problematic networks
    try:
        client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(verify=False)
        )
    except Exception as e:
        error_msg = f"⚠️ **Error initializing OpenAI client:** {str(e)}"
        yield error_msg
        return
    
    # Get equipment information
    equipment_info = get_equipment_summary()
    
    # Backend-controlled system prompt (can be modified in backend)
    current_language = st.session_state["language"]
    
    # Language-specific system prompts (controlled from backend)
    system_prompts = {
        "English": f"You are MyGymBro's AI workout planner for students. Your PRIMARY function is to create detailed, practical workout routines using ONLY the available gym equipment. Focus on creating complete workout plans with specific exercises, sets, reps, and rest periods.\n\nAvailable gym equipment:\n{equipment_info}\n\nWhen creating workout routines:\n- Use ONLY the equipment listed above\n- Provide specific sets, reps, and rest periods\n- Include proper warm-up and cool-down\n- Consider the user's fitness level and experience\n- Make routines practical for students with limited time\n- Explain proper form for each exercise\n- Suggest weight ranges based on available equipment\n- IMPORTANT: Format exercises clearly with numbered format (1. Exercise Name, 2. Exercise Name, etc.)\n- For each exercise, provide: name, sets/reps, description, how to perform it, and proper form tips\n\nFor weekly workout splits:\n- Plan out each day of the week (Monday-Sunday)\n- Include rest days for recovery\n- Balance muscle groups throughout the week\n- Consider the user's exercise frequency\n- Provide progression recommendations\n- Include variety to prevent boredom\n\nFor sports-specific training:\n- Consider the user's sports/activities when creating workouts\n- Include sport-specific exercises and movements\n- Balance gym training with sport performance\n- Focus on injury prevention for their specific sports\n- Suggest complementary exercises that enhance sport performance\n\nYou can also provide basic nutrition advice and calorie calculations when asked. Respond in English.",
        "French": f"Vous êtes le planificateur d'entraînements IA de MyGymBro pour les étudiants. Votre FONCTION PRINCIPALE est de créer des routines d'entraînement détaillées et pratiques en utilisant UNIQUEMENT l'équipement de gym disponible. Concentrez-vous sur la création de plans d'entraînement complets avec des exercices spécifiques, des séries, des répétitions et des périodes de repos.\n\nÉquipement de gym disponible:\n{equipment_info}\n\nLors de la création de routines d'entraînement:\n- Utilisez UNIQUEMENT l'équipement listé ci-dessus\n- Fournissez des séries, répétitions et périodes de repos spécifiques\n- Incluez un échauffement et une récupération appropriés\n- Considérez le niveau de forme et l'expérience de l'utilisateur\n- Rendez les routines pratiques pour les étudiants avec un temps limité\n- Expliquez la forme appropriée pour chaque exercice\n- Suggérez des plages de poids basées sur l'équipement disponible\n- IMPORTANT: Formatez les exercices clairement avec un format numéroté (1. Nom de l'exercice, 2. Nom de l'exercice, etc.)\n- Pour chaque exercice, fournissez: nom, séries/reps, description, comment l'effectuer, et conseils de forme appropriée\n\nPour les splits d'entraînement hebdomadaires:\n- Planifiez chaque jour de la semaine (lundi-dimanche)\n- Incluez des jours de repos pour la récupération\n- Équilibrez les groupes musculaires tout au long de la semaine\n- Considérez la fréquence d'exercice de l'utilisateur\n- Fournissez des recommandations de progression\n- Incluez de la variété pour éviter l'ennui\n\nVous pouvez aussi fournir des conseils nutritionnels de base et des calculs de calories quand demandé. Répondez en français.",
        "Korean": f"당신은 MyGymBro의 학생용 AI 운동 계획자입니다. 당신의 주요 기능은 사용 가능한 짐 기구만을 사용하여 상세하고 실용적인 운동 루틴을 만드는 것입니다. 구체적인 운동, 세트, 반복 횟수, 휴식 시간이 포함된 완전한 운동 계획을 만드는 데 집중하세요.\n\n사용 가능한 짐 기구:\n{equipment_info}\n\n운동 루틴을 만들 때:\n- 위에 나열된 기구만 사용하세요\n- 구체적인 세트, 반복 횟수, 휴식 시간을 제공하세요\n- 적절한 워밍업과 쿨다운을 포함하세요\n- 사용자의 체력 수준과 경험을 고려하세요\n- 시간이 제한된 학생들에게 실용적인 루틴을 만드세요\n- 각 운동의 올바른 자세를 설명하세요\n- 사용 가능한 기구를 바탕으로 무게 범위를 제안하세요\n- 중요: 운동을 명확하게 번호 형식으로 작성하세요 (1. 운동 이름, 2. 운동 이름 등)\n- 각 운동에 대해 제공: 이름, 세트/반복, 설명, 수행 방법, 올바른 자세 팁\n\n요청받을 때 기본적인 영양 조언과 칼로리 계산도 제공할 수 있습니다. 한국어로 답변해주세요.",
        "Mandarin": f"你是MyGymBro的学生AI健身计划制定者。你的主要功能是仅使用可用的健身房设备创建详细、实用的锻炼计划。专注于创建包含具体练习、组数、次数和休息时间的完整锻炼计划。\n\n可用健身房设备：\n{equipment_info}\n\n制定锻炼计划时：\n- 仅使用上述列出的设备\n- 提供具体的组数、次数和休息时间\n- 包括适当的热身和冷却\n- 考虑用户的健身水平和经验\n- 为时间有限的学生制定实用的计划\n- 解释每个练习的正确姿势\n- 根据可用设备建议重量范围\n- 重要：使用编号格式清楚地格式化练习（1. 练习名称，2. 练习名称等）\n- 对于每个练习，提供：名称、组数/次数、描述、如何执行以及正确的姿势提示\n\n被询问时也可以提供基本营养建议和卡路里计算。请用中文回答。",
        "Spanish": f"Eres el planificador de entrenamientos IA de MyGymBro para estudiantes. Tu FUNCIÓN PRINCIPAL es crear rutinas de entrenamiento detalladas y prácticas usando ÚNICAMENTE el equipamiento de gimnasio disponible. Enfócate en crear planes de entrenamiento completos con ejercicios específicos, series, repeticiones y períodos de descanso.\n\nEquipamiento de gimnasio disponible:\n{equipment_info}\n\nAl crear rutinas de entrenamiento:\n- Usa ÚNICAMENTE el equipamiento listado arriba\n- Proporciona series, repeticiones y períodos de descanso específicos\n- Incluye calentamiento y enfriamiento apropiados\n- Considera el nivel de fitness y experiencia del usuario\n- Haz rutinas prácticas para estudiantes con tiempo limitado\n- Explica la forma correcta para cada ejercicio\n- Sugiere rangos de peso basados en el equipamiento disponible\n- IMPORTANTE: Formatea los ejercicios claramente con formato numerado (1. Nombre del ejercicio, 2. Nombre del ejercicio, etc.)\n- Para cada ejercicio, proporciona: nombre, series/repeticiones, descripción, cómo realizarlo y consejos de forma apropiada\n\nTambién puedes proporcionar consejos nutricionales básicos y cálculos de calorías cuando se te pida. Responde en español."
    }
    
    system_prompt = system_prompts.get(current_language, system_prompts["English"])
    
    # Use streaming API with error handling
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.4,
            max_tokens=1000,
            stream=True  # Enable streaming
        )
        
        # Generator function that yields tokens as they arrive
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield content
    except Exception as e:
        error_type = type(e).__name__
        if "AuthenticationError" in error_type or "401" in str(e) or "invalid_api_key" in str(e):
            # Mark error state
            st.session_state["api_key_error"] = True
            # Show minimal error message
            error_msg = (
                "⚠️ **Unable to connect to OpenAI**\n\n"
                "Please verify your API key is correct and active. "
                "Update your `.env` file and restart Streamlit if needed."
            )
            yield error_msg
        else:
            error_msg = f"⚠️ **Error:** {str(e)[:200]}"
            yield error_msg

# Check authentication
check_authentication()

# Get user data from session state
user_data = st.session_state.get("user_data", {}) or {}

# Main UI
st.markdown(f'<h1 class="main-header">💪 {get_text("app_title")}</h1>', unsafe_allow_html=True)

# Welcome message with user's first name
user_first_name = user_data.get("first_name", "there")
st.markdown(f"""
<div class="fitness-card">
    <h3>🎓 Welcome, {user_first_name}!</h3>
    <p>{get_text("subtitle")}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # User info section
    if st.session_state.get("user_data"):
        user_data = st.session_state["user_data"]
        st.markdown("### 👤 User Profile")
        st.markdown(f"**Name:** {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
        st.markdown(f"**Email:** {st.session_state['user_email']}")
        st.markdown(f"**Fitness Level:** {user_data.get('fitness_level', 'Not specified')}")
        
        # Display current weight and measurements
        current_weight = user_data.get('weight_lbs', 'N/A')
        if current_weight != 'N/A':
            st.markdown(f"**Current Weight:** {current_weight} lbs")
        
        # Display muscle measurements if available
        muscle_measurements = user_data.get('muscle_measurements', {})
        if muscle_measurements:
            st.markdown("**Muscle Measurements:**")
            for muscle, measurement in muscle_measurements.items():
                st.markdown(f"  - {muscle.replace('_', ' ').title()}: {measurement} inches")
        
        st.markdown("---")
        
        # Update Weight and Measurements Button - Navigate to update profile page
        if st.button("📏 Update Weight & Measurements", use_container_width=True):
            st.switch_page("pages/4_update_profile.py")
        
        # Visual Body Fat Percentage Estimator Section
        st.markdown("---")
        with st.expander("📊 Visual Body Fat Percentage Estimator", expanded=False):
            # Display current body fat if available
            if 'body_fat_percentage' in user_data:
                current_bf = user_data['body_fat_percentage']
                category, color = get_body_fat_category(current_bf, user_data.get('gender', 'Male'))
                
                st.markdown(f"### Current Body Fat: {current_bf}%")
                st.markdown(f"**Category:** <span style='color: {color}; font-weight: bold;'>{category}</span>", unsafe_allow_html=True)
                
                # Visual progress bar
                if user_data.get('gender', 'Male').lower() in ['male', 'm']:
                    max_range = 32
                else:
                    max_range = 38
                
                bf_progress = min(current_bf / max_range, 1.0)
                st.progress(bf_progress)
                
                st.markdown("---")
            
            st.markdown("### Estimate Your Body Fat Percentage")
            st.markdown("*Compare yourself visually to the descriptions below, or enter an estimate directly*")
            
            user_gender = user_data.get('gender', 'Male')
            
            # Visual reference guide
            if user_gender.lower() in ['male', 'm']:
                st.markdown("#### 👨 Male Body Fat Reference Guide")
                body_fat_ranges_male = {
                    "Essential Fat (3-5%)": {
                        "range": (3, 5),
                        "color": "#4CAF50",
                        "description": "✅ Athletes at peak condition. Very defined muscle separation, vascularity visible. Minimal fat."
                    },
                    "Athletes (6-13%)": {
                        "range": (6, 13),
                        "color": "#8BC34A",
                        "description": "✅ Excellent condition. Visible abs, good muscle definition. Low body fat."
                    },
                    "Fitness (14-17%)": {
                        "range": (14, 17),
                        "color": "#CDDC39",
                        "description": "✅ Good shape. Some abs visible, slight fat layer. Athletic build."
                    },
                    "Average (18-24%)": {
                        "range": (18, 24),
                        "color": "#FFC107",
                        "description": "⚠️ Normal range. Some fat, less muscle definition. Abs may not be visible."
                    },
                    "Obese (25-31%)": {
                        "range": (25, 31),
                        "color": "#FF9800",
                        "description": "❌ Higher body fat. Noticeable fat deposits, less muscle definition."
                    },
                    "Very High (32%+)": {
                        "range": (32, 50),
                        "color": "#F44336",
                        "description": "❌ High body fat. Significant fat deposits, minimal muscle visibility."
                    }
                }
            else:
                st.markdown("#### 👩 Female Body Fat Reference Guide")
                body_fat_ranges_male = {
                    "Essential Fat (10-13%)": {
                        "range": (10, 13),
                        "color": "#4CAF50",
                        "description": "✅ Athletes at peak condition. Very defined muscles, minimal fat."
                    },
                    "Athletes (14-20%)": {
                        "range": (14, 20),
                        "color": "#8BC34A",
                        "description": "✅ Excellent condition. Visible muscle definition, low body fat."
                    },
                    "Fitness (21-24%)": {
                        "range": (21, 24),
                        "color": "#CDDC39",
                        "description": "✅ Good shape. Some muscle definition, slight fat layer."
                    },
                    "Average (25-31%)": {
                        "range": (25, 31),
                        "color": "#FFC107",
                        "description": "⚠️ Normal range. Moderate fat, less muscle definition."
                    },
                    "Obese (32-37%)": {
                        "range": (32, 37),
                        "color": "#FF9800",
                        "description": "❌ Higher body fat. Noticeable fat deposits."
                    },
                    "Very High (38%+)": {
                        "range": (38, 50),
                        "color": "#F44336",
                        "description": "❌ High body fat. Significant fat deposits."
                    }
                }
            
            # Display reference guide
            for category_name, info in body_fat_ranges_male.items():
                low, high = info["range"]
                st.markdown(
                    f"""
                    <div style='
                        background: {info["color"]}20;
                        border-left: 4px solid {info["color"]};
                        padding: 10px;
                        margin: 10px 0;
                        border-radius: 5px;
                    '>
                        <strong style='color: {info["color"]};'>{category_name} ({low}-{high}%)</strong><br/>
                        <small>{info["description"]}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown("---")
            
            estimation_method = st.radio(
                "Estimation Method:",
                ["Select from Visual Categories", "Enter Percentage Directly"],
                key="bf_est_method"
            )
            
            # Helper function to display visual chart
            def display_body_fat_chart(body_fat, gender, category, color):
                """Display visual body fat percentage chart."""
                if gender.lower() in ['male', 'm']:
                    max_range = 32
                    categories_display = {
                        "Essential Fat": (0, 6, "#4CAF50"),
                        "Athletes": (6, 14, "#8BC34A"),
                        "Fitness": (14, 18, "#CDDC39"),
                        "Average": (18, 25, "#FFC107"),
                        "Obese": (25, 32, "#FF9800"),
                        "Very High": (32, 100, "#F44336")
                    }
                else:
                    max_range = 38
                    categories_display = {
                        "Essential Fat": (0, 14, "#4CAF50"),
                        "Athletes": (14, 21, "#8BC34A"),
                        "Fitness": (21, 25, "#CDDC39"),
                        "Average": (25, 32, "#FFC107"),
                        "Obese": (32, 38, "#FF9800"),
                        "Very High": (38, 100, "#F44336")
                    }
                
                # Visual bar chart - HTML/CSS based
                html_chart = f"""
                <div style='margin: 20px 0;'>
                    <div style='position: relative; height: 80px; background: #f0f0f0; border-radius: 10px; overflow: hidden; border: 2px solid #ddd;'>
                """
                
                x_pos = 0
                for cat_name, (low, high, cat_color) in categories_display.items():
                    width = high - low
                    width_percent = (width / max_range) * 100
                    left_percent = (x_pos / max_range) * 100
                    
                    is_current = body_fat >= low and body_fat < high
                    opacity = 1.0 if is_current else 0.5
                    
                    html_chart += f"""
                        <div style='
                            position: absolute;
                            left: {left_percent}%;
                            width: {width_percent}%;
                            height: 100%;
                            background: {cat_color};
                            opacity: {opacity};
                            border-right: 2px solid rgba(0,0,0,0.1);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            text-align: center;
                            font-size: 10px;
                            font-weight: bold;
                            color: {'white' if is_current else '#333'};
                        '>
                            <div style='padding: 5px;'>
                                {cat_name}<br/>
                                <small>({low}-{high}%)</small>
                            </div>
                        </div>
                    """
                    x_pos += width
                
                # Mark current position
                marker_position = (body_fat / max_range) * 100
                html_chart += f"""
                        <div style='
                            position: absolute;
                            left: {marker_position}%;
                            top: 50%;
                            transform: translate(-50%, -50%);
                            width: 20px;
                            height: 20px;
                            background: white;
                            border: 3px solid #000;
                            border-radius: 50%;
                            z-index: 10;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                        '></div>
                    </div>
                    <div style='text-align: center; margin-top: 10px; font-weight: bold; color: #666;'>
                        Body Fat Percentage: <span style='color: {color}; font-size: 1.2em;'>{body_fat}%</span>
                    </div>
                </div>
                """
                
                st.markdown(html_chart, unsafe_allow_html=True)
            
            if estimation_method == "Select from Visual Categories":
                with st.form("body_fat_category_form"):
                    st.info("💡 Look at the reference guide above and select the category that best matches your current body appearance.")
                    
                    # Create category options based on gender
                    if user_gender.lower() in ['male', 'm']:
                        category_options = [
                            "Essential Fat (3-5%)",
                            "Athletes (6-13%)",
                            "Fitness (14-17%)",
                            "Average (18-24%)",
                            "Obese (25-31%)",
                            "Very High (32%+)"
                        ]
                        default_index = 3  # Average
                    else:
                        category_options = [
                            "Essential Fat (10-13%)",
                            "Athletes (14-20%)",
                            "Fitness (21-24%)",
                            "Average (25-31%)",
                            "Obese (32-37%)",
                            "Very High (38%+)"
                        ]
                        default_index = 3  # Average
                    
                    # Pre-select current category if available
                    current_bf = user_data.get('body_fat_percentage')
                    if current_bf:
                        for i, option in enumerate(category_options):
                            # Extract range from option
                            if user_gender.lower() in ['male', 'm']:
                                ranges = [(3, 5), (6, 13), (14, 17), (18, 24), (25, 31), (32, 50)]
                            else:
                                ranges = [(10, 13), (14, 20), (21, 24), (25, 31), (32, 37), (38, 50)]
                            
                            low, high = ranges[i]
                            if low <= current_bf <= high:
                                default_index = i
                                break
                    
                    selected_category = st.selectbox(
                        "Select your body fat category:",
                        category_options,
                        index=default_index,
                        key="bf_category_select"
                    )
                    
                    estimate_button = st.form_submit_button("💾 Save Visual Estimate", use_container_width=True)
                    
                    if estimate_button:
                        # Extract body fat percentage from selected category
                        if user_gender.lower() in ['male', 'm']:
                            category_to_range = {
                                "Essential Fat (3-5%)": (3, 5),
                                "Athletes (6-13%)": (6, 13),
                                "Fitness (14-17%)": (14, 17),
                                "Average (18-24%)": (18, 24),
                                "Obese (25-31%)": (25, 31),
                                "Very High (32%+)": (32, 50)
                            }
                        else:
                            category_to_range = {
                                "Essential Fat (10-13%)": (10, 13),
                                "Athletes (14-20%)": (14, 20),
                                "Fitness (21-24%)": (21, 24),
                                "Average (25-31%)": (25, 31),
                                "Obese (32-37%)": (32, 37),
                                "Very High (38%+)": (38, 50)
                            }
                        
                        low, high = category_to_range[selected_category]
                        # Use middle of the range as estimate
                        body_fat = round((low + high) / 2, 1)
                        category, color = get_body_fat_category(body_fat, user_gender)
                        
                        # Save to user profile
                        updated_data = {'body_fat_percentage': body_fat}
                        if update_user_profile(st.session_state['user_email'], updated_data):
                            st.success(f"✅ Body Fat Percentage estimated: **{body_fat}%**")
                            st.markdown(f"**Category:** <span style='color: {color}; font-weight: bold;'>{category}</span>", unsafe_allow_html=True)
                            
                            # Display visual chart
                            display_body_fat_chart(body_fat, user_gender, category, color)
                            
                            st.rerun()
                        else:
                            st.error("❌ Failed to save estimate. Please try again.")
            
            else:  # Enter Percentage Directly
                with st.form("body_fat_direct_form"):
                    st.info("💡 Enter your estimated body fat percentage directly (based on visual appearance or previous measurements).")
                    
                    # Get current body fat or default
                    current_bf = user_data.get('body_fat_percentage', 20.0)
                    
                    body_fat_input = st.number_input(
                        "Body Fat Percentage (%)",
                        min_value=3.0,
                        max_value=50.0,
                        value=float(current_bf),
                        step=0.1,
                        help="Enter your estimated body fat percentage (3-50%)",
                        key="bf_direct_input"
                    )
                    
                    estimate_button = st.form_submit_button("💾 Save Estimate", use_container_width=True)
                    
                    if estimate_button:
                        body_fat = round(body_fat_input, 1)
                        category, color = get_body_fat_category(body_fat, user_gender)
                        
                        # Save to user profile
                        updated_data = {'body_fat_percentage': body_fat}
                        if update_user_profile(st.session_state['user_email'], updated_data):
                            st.success(f"✅ Body Fat Percentage saved: **{body_fat}%**")
                            st.markdown(f"**Category:** <span style='color: {color}; font-weight: bold;'>{category}</span>", unsafe_allow_html=True)
                            
                            # Display visual chart
                            display_body_fat_chart(body_fat, user_gender, category, color)
                            
                            st.rerun()
                        else:
                            st.error("❌ Failed to save estimate. Please try again.")
        
        st.markdown("---")
    
    st.markdown("### 🎛️ Settings")
    
    # Language selector
    language_options = ["English", "French", "Korean", "Mandarin", "Spanish"]
    selected_language = st.selectbox(
        f"🌍 {get_text('select_language')}",
        language_options,
        index=language_options.index(st.session_state["language"])
    )
    
    # Update language if changed
    if selected_language != st.session_state["language"]:
        st.session_state["language"] = selected_language
        st.rerun()
    
    # Clear history button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
    
    st.markdown("---")
    
    # Set default prompt mode (controlled from backend)
    selected_prompt = "Basic Mode"  # Default mode, can be changed in backend
    
    # Get additional user data for workout generation
    age = user_data.get("age", 20)
    gender = user_data.get("gender", "Male")
    fitness_level = user_data.get("fitness_level", "Average")
    exercise_frequency = user_data.get("exercise_frequency", "3x/week")
    sports_activities = user_data.get("sports_activities", [])
    
    # Workout Plan Generator Buttons in Sidebar
    st.markdown("### 🏋️ Workout Plans")
    st.markdown("*Click to generate workout routines*")
    
    # Custom workout button - Navigate to custom workout page
    user_first_name = user_data.get("first_name", "U")
    if st.button(f"✨ Custom workout for {user_first_name}", use_container_width=True):
        st.switch_page("pages/5_custom_workout.py")
    
    st.markdown("---")
    
    # Quick workout plan buttons
    with st.expander("💪 Basic Workouts", expanded=True):
        if st.button("💪 Full Body Workout", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a full body workout routine for me using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on compound movements and include proper warm-up and cool-down."
            st.rerun()
        
        if st.button("🔥 Upper Body Focus", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create an upper body focused workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include chest, back, shoulders, and arms exercises."
            st.rerun()
        
        if st.button("🦵 Lower Body Focus", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a lower body focused workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include legs, glutes, and core exercises."
            st.rerun()
        
        if st.button("📅 Full Weekly Split", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a complete weekly workout split for me using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Plan out each day of the week with specific exercises, sets, reps, and rest days. Make it a balanced program that targets all muscle groups throughout the week."
            st.rerun()
        
        if st.button("⚡ Quick 30-min Workout", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a quick 30-minute workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Make it efficient and effective for busy students."
            st.rerun()
        
        if st.button("🏃 Cardio + Strength", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a cardio and strength combined workout using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include both cardio and strength training elements."
            st.rerun()
    
    with st.expander("🎯 Advanced Workouts", expanded=False):
        if st.button("🎯 Beginner-Friendly", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a beginner-friendly workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, beginner fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on proper form and progression."
            st.rerun()
        
        if st.button("💪 Push/Pull/Legs Split", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a push/pull/legs workout split using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include push day (chest, shoulders, triceps), pull day (back, biceps), and legs day with proper rest between muscle groups."
            st.rerun()
        
        if st.button("🔥 High Intensity Training", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a high intensity training (HIT) workout using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on maximum effort with shorter rest periods and higher intensity."
            st.rerun()
    
    with st.expander("😂 Fun & Meme Workouts", expanded=False):
        if st.button("😭 Man United Fan Workout", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a funny workout routine for a Manchester United fan who's been crying all day about their team's performance. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Make it therapeutic and include exercises that help with emotional stress relief, like heavy lifting to channel frustration, cardio to sweat out the tears, and maybe some yoga for inner peace. Add some humor and motivation!"
            st.rerun()
        
        if st.button("👑 Clash Royale Rage Workout", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a workout routine for someone who gets mad at MegaKnight in Clash Royale. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include explosive movements to channel the rage, cardio to burn off the frustration, and strength training to feel powerful. Make it fun and include some gaming references!"
            st.rerun()
        
        if st.button("🎮 Gamer's Revenge Workout", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a workout for a gamer who needs to get revenge on their opponents. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on building strength and endurance to dominate in both real life and gaming. Include exercises that improve hand-eye coordination and reaction time!"
            st.rerun()
        
        if st.button("🍕 Pizza Recovery Workout", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a workout routine for someone who ate too much pizza and needs to burn it off. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on cardio and core exercises to work off those extra calories, but make it fun and not too intense since I'm probably feeling sluggish!"
            st.rerun()
        
        if st.button("😴 Lazy Day Motivation", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a gentle but effective workout for someone having a lazy day but still wants to move. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Make it easy to start but progressively engaging, with lots of motivation and encouragement!"
            st.rerun()
        
        if st.button("🎯 Procrastination Fighter", use_container_width=True):
            sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
            st.session_state["pre_filled_question"] = f"Create a workout routine for someone who's procrastinating on their studies/work and needs to get moving. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Make it energizing and motivating, with exercises that help clear the mind and boost productivity!"
            st.rerun()
    
    # Clash Royale themed workouts (only for Clash Royale players)
    if st.session_state.get("user_email") == "clashroyale.player@mygymbro.com":
        with st.expander("👑 Clash Royale Themed", expanded=False):
            if st.button("🛡️ MegaKnight's Rage Workout", use_container_width=True):
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                st.session_state["pre_filled_question"] = f"Create a MegaKnight-themed workout routine! I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. MegaKnight is all about explosive power and heavy hits, so include exercises that build explosive strength, heavy lifting, and powerful movements. Think jumping exercises, heavy squats, and explosive push-ups. Make it intense and rage-filled like when MegaKnight drops on your troops!"
                st.rerun()
            
            if st.button("⚔️ P.E.K.K.A.'s Armor Workout", use_container_width=True):
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                st.session_state["pre_filled_question"] = f"Create a P.E.K.K.A.-themed workout routine! I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. P.E.K.K.A. is the ultimate tank with heavy armor, so focus on building massive strength, endurance, and that tank-like physique. Include heavy compound movements, long sets, and exercises that make you feel like an unstoppable armored warrior. Think deadlifts, heavy presses, and endurance challenges!"
                st.rerun()
            
            if st.button("👑 King's Royal Workout", use_container_width=True):
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                st.session_state["pre_filled_question"] = f"Create a King-themed workout routine! I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. The King is the leader of the arena, so this should be a royal, comprehensive workout that covers all aspects of fitness. Include exercises that build strength, agility, and royal presence. Think full-body movements, balance exercises, and workouts that make you feel like the ruler of the gym!"
                st.rerun()
            
            if st.button("🏹 Archer Queen's Precision", use_container_width=True):
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                st.session_state["pre_filled_question"] = f"Create an Archer Queen-themed workout routine! I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. The Archer Queen is all about precision, agility, and long-range power. Focus on exercises that improve coordination, balance, and upper body strength. Include exercises that require precision and control, like single-arm movements, balance challenges, and core stability work!"
                st.rerun()
            
            if st.button("⚡ Sparky's Electric Power", use_container_width=True):
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                st.session_state["pre_filled_question"] = f"Create a Sparky-themed workout routine! I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Sparky charges up for massive damage, so this workout should focus on explosive power and high-intensity bursts. Include exercises that build explosive strength, like plyometrics, sprint intervals, and exercises that require maximum effort in short bursts. Make it electric and high-energy!"
                st.rerun()
            
            if st.button("🏰 X-Bow's Tower Defense", use_container_width=True):
                sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
                st.session_state["pre_filled_question"] = f"Create an X-Bow-themed workout routine! I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. The X-Bow is a defensive building that requires stability and endurance. Focus on exercises that build stability, endurance, and defensive strength. Include isometric holds, endurance exercises, and movements that require sustained effort. Think planks, wall sits, and long-duration exercises!"
                st.rerun()
    
    st.markdown("---")
    
    # Additional Tools
    st.markdown("### 📊 Additional Tools")
    if st.button("🔥 Calculate my maintenance calories", use_container_width=True):
        st.session_state["show_calorie_calculation"] = True
        st.rerun()
    
    if st.button("💬 Ask MyGymBro anything", use_container_width=True):
        st.session_state["pre_filled_question"] = "I have a question about my fitness routine or nutrition. Please help me with personalized advice based on my information."
        st.rerun()

# Get additional user data for workout generation (for use in main area if needed)
user_data = st.session_state.get("user_data", {}) or {}
age = user_data.get("age", 20)
gender = user_data.get("gender", "Male")
fitness_level = user_data.get("fitness_level", "Average")
exercise_frequency = user_data.get("exercise_frequency", "3x/week")
sports_activities = user_data.get("sports_activities", [])

# Main area - Chat interface only
st.markdown("### 💬 Chat with MyGymBro")
st.markdown("*Use the sidebar buttons to generate workout plans or type your own questions*")

# Calorie calculation using user data from session state
if st.session_state.get("show_calorie_calculation", False):
    # Get user data
    height_cm = user_data.get("height_cm", 175)  # Default height in cm
    weight_kg = user_data.get("weight_kg", 70)   # Default weight in kg
    lifestyle = user_data.get("lifestyle", "Student or office worker")
    
    # Calculate BMR using user data
    bmr = calculate_bmr(gender, age, height_cm, weight_kg)
    
    # Calculate activity multiplier
    activity_multiplier = calculate_activity_multiplier(lifestyle, exercise_frequency, fitness_level)
    
    # Calculate total metabolism
    activity_metabolism = round(bmr * (activity_multiplier - 1), 1)
    total_metabolism = round(bmr * activity_multiplier, 1)
    
    # Store calculation results in session state
    st.session_state["calorie_results"] = {
        "bmr": bmr,
        "activity_metabolism": activity_metabolism,
        "total_metabolism": total_metabolism,
        "age": age,
        "fitness_level": fitness_level
    }
    st.session_state["show_results"] = True
    st.session_state["show_calorie_calculation"] = False

# Show results section
if st.session_state.get("show_results", False) and st.session_state.get("calorie_results"):
    results = st.session_state["calorie_results"]
    
    # Display results
    st.markdown("### 📊 " + get_text("maintenance_calories"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(get_text("bmr"), f"{results['bmr']} kcal")
    with col2:
        st.metric(get_text("activity_metabolism"), f"{results['activity_metabolism']} kcal")
    with col3:
        st.metric(get_text("total_metabolism"), f"{results['total_metabolism']} kcal")
    
    # Goal selection
    st.markdown("### 🎯 " + get_text("daily_intake"))
    goal = st.radio("Select your goal:", ["weight_loss", "weight_maintenance", "bulk_up"], 
                   format_func=lambda x: get_text(x), key="goal_selection")
    
    # Calculate macros based on selected goal
    macros = calculate_macros(results['total_metabolism'], goal)
    
    st.markdown(f"**{get_text('target_calories')}:** {macros['calories']} kcal")
    
    # Macronutrients
    st.markdown("### 🥗 " + get_text("macros"))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(get_text("carbs"), f"{macros['carbs']}g")
    with col2:
        st.metric(get_text("protein"), f"{macros['protein']}g")
    with col3:
        st.metric(get_text("fat"), f"{macros['fat']}g")
    
    # Heart rate range
    min_hr, max_hr = calculate_heart_rate_range(results['age'], results['fitness_level'])
    st.markdown("### ❤️ " + get_text("cardio_intensity"))
    st.markdown(f"**{get_text('heart_rate_range')}:** {min_hr} - {max_hr} {get_text('bpm')}")
    st.info("💡 This is the optimal heart rate range for fat burning during cardio!")
    
    # Close results button
    if st.button("❌ Close Results", key="close_results"):
        st.session_state["show_results"] = False
        st.session_state["calorie_results"] = None
        st.rerun()

st.markdown("---")

# Display chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        # Check if this is an assistant message that might contain a workout
        if message["role"] == "assistant":
            content = message["content"]
            # Check if content looks like a workout (contains exercise-related keywords)
            workout_keywords = ['workout', 'exercise', 'routine', 'sets', 'reps', 'squat', 'press', 'deadlift', 'bench']
            is_workout = any(keyword in content.lower() for keyword in workout_keywords)
            
            if is_workout:
                # Try to display as workout blocks
                displayed_as_blocks = display_workout_blocks(content)
                if not displayed_as_blocks:
                    # If parsing failed, display as regular text
                    st.write(content)
            else:
                # Not a workout, display as regular text
                st.write(content)
        else:
            # User message, display normally
            st.write(message["content"])

# Show API key error warning (dismissible)
if st.session_state.get("api_key_error", False) and not st.session_state.get("api_error_dismissed", False):
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.warning("⚠️ API Key Issue: Your OpenAI API key appears invalid. Please check your `.env` file and restart Streamlit.")
        with col2:
            if st.button("Dismiss", key="dismiss_api_error"):
                st.session_state["api_error_dismissed"] = True
                st.rerun()

# Show helpful message if there are messages
if st.session_state["messages"]:
    st.info("💡 You can keep asking follow-up questions! Ask for modifications, more details, or different workout variations.")

# Handle pre-filled questions
user_input = None
if "pre_filled_question" in st.session_state and st.session_state["pre_filled_question"]:
    user_input = st.session_state["pre_filled_question"]
    is_custom_workout = st.session_state.get("custom_workout_request", False)
    st.session_state["pre_filled_question"] = None  # Clear after use
    st.session_state["prefilled_triggered"] = True  # Flag to track pre-filled question
    
    # Store the actual prompt for AI (even if we show a different message to user)
    if is_custom_workout:
        # Store actual prompt for AI, but show friendly message to user
        st.session_state["actual_ai_prompt"] = user_input  # Store the real prompt
        st.session_state["messages"].append({"role": "user", "content": "🤔 MyGymBro is thinking..."})
        st.session_state["custom_workout_request"] = False  # Clear flag
    else:
        st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Force rerun to show the user message in chat first
    st.rerun()
elif user_input := st.chat_input(get_text("chat_placeholder")):
    # Add user message to session state first (this will show in chat immediately after rerun)
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Force rerun to show the user message in chat first
    st.rerun()

# Generate AI response if there's a user message without an assistant response
if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
    # Get the last user message - use actual prompt if it's a custom workout
    if "actual_ai_prompt" in st.session_state:
        last_user_message = st.session_state["actual_ai_prompt"]
        del st.session_state["actual_ai_prompt"]  # Clear after use
    else:
        last_user_message = st.session_state["messages"][-1]["content"]
    
    # Create a placeholder for the assistant message
    with st.chat_message("assistant"):
        # Use write_stream to stream the response word by word
        # This displays the response progressively as tokens arrive
        full_response = st.write_stream(get_ai_response_stream(last_user_message, selected_prompt))
    
    # Add AI response to session state after streaming completes
    # This ensures the message persists in the chat history
    st.session_state["messages"].append({"role": "assistant", "content": full_response})
    
    # Rerun to update the UI and ensure the message is saved properly
    # The streamed content will now be displayed from session_state on next render
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        💪 {get_text('footer')}<br>
        <small>{get_text('footer_subtitle')}</small>
    </div>
    """, 
    unsafe_allow_html=True
)
