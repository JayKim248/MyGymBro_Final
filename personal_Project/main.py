import streamlit as st
from dotenv import load_dotenv
import json
from pathlib import Path
import os
from openai import OpenAI
import pandas as pd

# Load environment variables
load_dotenv()

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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "language" not in st.session_state:
    st.session_state["language"] = "English"

# Data directory setup
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USER_PROFILE_PATH = DATA_DIR / "user_profiles.json"
EQUIPMENT_FILE = DATA_DIR / "GymMachineList.xlsx"

# Translation dictionaries
TRANSLATIONS = {
    "English": {
        "app_title": "MyGymBro - Student Gym Routine Builder",
        "welcome": "Welcome to MyGymBro! 💪",
        "subtitle": "Your AI-powered gym routine builder for students",
        "routine_calculator": "Routine Set Calculator",
        "number_input": "Enter number (1 to n)",
        "calculate": "Calculate",
        "calorie_calculator": "Calorie Calculator",
        "gender": "Gender",
        "age": "Age",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "lifestyle": "Lifestyle",
        "exercise_experience": "Exercise Experience",
        "exercise_frequency": "Exercise Frequency",
        "fitness_level": "Fitness Level",
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
        "chat_placeholder": "💬 Ask about gym routines or exercises!",
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
        "routine_calculator": "Calculateur de Série de Routine",
        "number_input": "Entrez un nombre (1 à n)",
        "calculate": "Calculer",
        "calorie_calculator": "Calculateur de Calories",
        "gender": "Sexe",
        "age": "Âge",
        "height": "Taille (cm)",
        "weight": "Poids (kg)",
        "lifestyle": "Mode de Vie",
        "exercise_experience": "Expérience d'Exercice",
        "exercise_frequency": "Fréquence d'Exercice",
        "fitness_level": "Niveau de Forme",
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
        "chat_placeholder": "💬 Posez des questions sur les routines de gym ou exercices!",
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
        "routine_calculator": "루틴 세트 계산기",
        "number_input": "숫자 입력 (1부터 n까지)",
        "calculate": "계산하기",
        "calorie_calculator": "칼로리 계산기",
        "gender": "성별",
        "age": "나이",
        "height": "키 (cm)",
        "weight": "몸무게 (kg)",
        "lifestyle": "생활습관",
        "exercise_experience": "운동 경력",
        "exercise_frequency": "운동 횟수",
        "fitness_level": "체력수준",
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
        "chat_placeholder": "💬 짐 루틴이나 운동에 대해 궁금한 것을 물어보세요!",
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
        "routine_calculator": "计划组计算器",
        "number_input": "输入数字（1到n）",
        "calculate": "计算",
        "calorie_calculator": "卡路里计算器",
        "gender": "性别",
        "age": "年龄",
        "height": "身高（厘米）",
        "weight": "体重（公斤）",
        "lifestyle": "生活方式",
        "exercise_experience": "运动经验",
        "exercise_frequency": "运动频率",
        "fitness_level": "健身水平",
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
        "chat_placeholder": "💬 询问健身计划或运动相关问题！",
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
        "routine_calculator": "Calculadora de Series de Rutina",
        "number_input": "Ingrese número (1 a n)",
        "calculate": "Calcular",
        "calorie_calculator": "Calculadora de Calorías",
        "gender": "Género",
        "age": "Edad",
        "height": "Altura (cm)",
        "weight": "Peso (kg)",
        "lifestyle": "Estilo de Vida",
        "exercise_experience": "Experiencia de Ejercicio",
        "exercise_frequency": "Frecuencia de Ejercicio",
        "fitness_level": "Nivel de Fitness",
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
        "chat_placeholder": "💬 ¡Pregunta sobre rutinas de gimnasio o ejercicios!",
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

# Utility function
def weird(num):
    digits = [int(d) for d in str(num)]
    add_on = sum(digits)
    return 1 if num % add_on == 0 else 0

def calculate_weird_numbers(n):
    result = 0
    for i in range(1, n + 1):
        result += weird(i)
    return result

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

# AI response function
def get_ai_response(question, prompt_type):
    import ssl
    import httpx
    
    # Create client with SSL verification disabled for problematic networks
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        http_client=httpx.Client(verify=False)
    )
    
    # Get equipment information
    equipment_info = get_equipment_summary()
    
    # Backend-controlled system prompt (can be modified in backend)
    current_language = st.session_state["language"]
    
    # Language-specific system prompts (controlled from backend)
    system_prompts = {
        "English": f"You are MyGymBro's student-exclusive AI gym routine builder. Create practical and sustainable gym routines that consider students' busy schedules, limited budgets, and various fitness levels.\n\nCurrent available equipment:\n{equipment_info}\n\nUse these equipment to create routines. Respond in English.",
        "French": f"Vous êtes le constructeur de routines de gym IA exclusif aux étudiants de MyGymBro. Créez des routines de gym pratiques et durables qui tiennent compte des emplois du temps chargés des étudiants, des budgets limités et des différents niveaux de forme.\n\nÉquipement actuellement disponible:\n{equipment_info}\n\nUtilisez cet équipement pour créer des routines. Répondez en français.",
        "Korean": f"당신은 MyGymBro의 학생 전용 AI 짐 루틴 빌더입니다. 학생들의 바쁜 일정, 제한된 예산, 다양한 체력 수준을 고려하여 실용적이고 지속 가능한 짐 루틴을 만들어주세요.\n\n현재 사용 가능한 기구 목록:\n{equipment_info}\n\n이 기구들을 활용하여 루틴을 만들어주세요. 한국어로 답변해주세요.",
        "Mandarin": f"你是MyGymBro的学生专用AI健身计划构建器。创建实用且可持续的健身计划，考虑学生的繁忙日程、有限预算和不同的健身水平。\n\n当前可用器械：\n{equipment_info}\n\n使用这些器械创建计划。请用中文回答。",
        "Spanish": f"Eres el constructor de rutinas de gimnasio IA exclusivo para estudiantes de MyGymBro. Crea rutinas de gimnasio prácticas y sostenibles que consideren los horarios ocupados de los estudiantes, presupuestos limitados y varios niveles de fitness.\n\nEquipamiento actualmente disponible:\n{equipment_info}\n\nUsa este equipamiento para crear rutinas. Responde en español."
    }
    
    system_prompt = system_prompts.get(current_language, system_prompts["English"])
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.4,
        max_tokens=1000
    )
    return response.choices[0].message.content

# Main UI
st.markdown(f'<h1 class="main-header">💪 {get_text("app_title")}</h1>', unsafe_allow_html=True)

# Welcome message
st.markdown(f"""
<div class="fitness-card">
    <h3>🎓 {get_text("welcome")}</h3>
    <p>{get_text("subtitle")}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ 설정")
    
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
    if st.button("🗑️ 대화 기록 지우기", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    
    st.markdown("---")
    
    # Set default prompt mode (controlled from backend)
    selected_prompt = "Basic Mode"  # Default mode, can be changed in backend
    
    # Calorie Calculator
    st.markdown(f"### 🔥 {get_text('calorie_calculator')}")
    
    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox(get_text("gender"), ["Male", "Female"])
        age = st.number_input(get_text("age"), min_value=10, max_value=100, value=20)
    with col2:
        height = st.number_input(get_text("height"), min_value=100, max_value=250, value=170)
        weight = st.number_input(get_text("weight"), min_value=30, max_value=200, value=70)
    
    lifestyle = st.selectbox(
        get_text("lifestyle"),
        ["Lying down 15+ hours", "Almost no movement at home", "Student or office worker", "Active", "Very active"]
    )
    
    col3, col4 = st.columns(2)
    with col3:
        exercise_experience = st.selectbox(
            get_text("exercise_experience"),
            ["Beginner", "1-3 years", "3-5 years intermediate", "5+ years advanced", "10+ years expert"]
        )
        exercise_frequency = st.selectbox(
            get_text("exercise_frequency"),
            ["None", "1x/week", "2x/week", "3x/week", "4x/week", "5x/week", "6x/week", "7x/week"]
        )
    with col4:
        fitness_level = st.selectbox(
            get_text("fitness_level"),
            ["Very poor", "Poor", "Below average", "Average", "Above average", "Good", "Very good"]
        )
    
    if st.button(f"🔥 {get_text('calculate_calories')}", use_container_width=True):
        # Calculate BMR
        bmr = calculate_bmr(gender, age, height, weight)
        
        # Calculate activity multiplier
        activity_multiplier = calculate_activity_multiplier(lifestyle, exercise_frequency, fitness_level)
        
        # Calculate total metabolism
        activity_metabolism = round(bmr * (activity_multiplier - 1), 1)
        total_metabolism = round(bmr * activity_multiplier, 1)
        
        # Display results
        st.markdown("### 📊 " + get_text("maintenance_calories"))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(get_text("bmr"), f"{bmr} kcal")
        with col2:
            st.metric(get_text("activity_metabolism"), f"{activity_metabolism} kcal")
        with col3:
            st.metric(get_text("total_metabolism"), f"{total_metabolism} kcal")
        
        # Goal selection
        st.markdown("### 🎯 " + get_text("daily_intake"))
        goal = st.radio("Select your goal:", ["weight_loss", "weight_maintenance", "bulk_up"], 
                       format_func=lambda x: get_text(x))
        
        # Calculate macros
        macros = calculate_macros(total_metabolism, goal)
        
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
        min_hr, max_hr = calculate_heart_rate_range(age, fitness_level)
        st.markdown("### ❤️ " + get_text("cardio_intensity"))
        st.markdown(f"**{get_text('heart_rate_range')}:** {min_hr} - {max_hr} {get_text('bpm')}")
        st.info("💡 This is the optimal heart rate range for fat burning during cardio!")
    
    st.markdown("---")
    
    # Weird number calculator
    st.markdown(f"**{get_text('routine_calculator')}**")
    n_input = st.number_input(get_text("number_input"), min_value=1, max_value=1000, value=10)
    if st.button(get_text("calculate")):
        result = calculate_weird_numbers(n_input)
        st.success(f"1부터 {n_input}까지의 weird number 개수: {result}")

# Main chat interface
st.markdown(f"### {get_text('chat_title')}")

# Display chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input(get_text("chat_placeholder"))

if user_input:
    # Display user message
    st.chat_message("user").write(user_input)
    
    # Get AI response
    try:
        with st.spinner(get_text("loading_message")):
            ai_answer = get_ai_response(user_input, selected_prompt)
        
        # Display AI response
        st.chat_message("assistant").write(ai_answer)
        
        # Add messages to session state
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "assistant", "content": ai_answer})
        
    except Exception as e:
        # Show a helpful message instead of error
        st.chat_message("assistant").write(get_text("error_message"))
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "assistant", "content": "Network connection issue - AI response unavailable."})

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