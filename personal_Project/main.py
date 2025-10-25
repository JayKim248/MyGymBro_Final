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
        "English": f"You are MyGymBro's AI workout planner for students. Your PRIMARY function is to create detailed, practical workout routines using ONLY the available gym equipment. Focus on creating complete workout plans with specific exercises, sets, reps, and rest periods.\n\nAvailable gym equipment:\n{equipment_info}\n\nWhen creating workout routines:\n- Use ONLY the equipment listed above\n- Provide specific sets, reps, and rest periods\n- Include proper warm-up and cool-down\n- Consider the user's fitness level and experience\n- Make routines practical for students with limited time\n- Explain proper form for each exercise\n- Suggest weight ranges based on available equipment\n\nFor weekly workout splits:\n- Plan out each day of the week (Monday-Sunday)\n- Include rest days for recovery\n- Balance muscle groups throughout the week\n- Consider the user's exercise frequency\n- Provide progression recommendations\n- Include variety to prevent boredom\n\nFor sports-specific training:\n- Consider the user's sports/activities when creating workouts\n- Include sport-specific exercises and movements\n- Balance gym training with sport performance\n- Focus on injury prevention for their specific sports\n- Suggest complementary exercises that enhance sport performance\n\nYou can also provide basic nutrition advice and calorie calculations when asked. Respond in English.",
        "French": f"Vous êtes le planificateur d'entraînements IA de MyGymBro pour les étudiants. Votre FONCTION PRINCIPALE est de créer des routines d'entraînement détaillées et pratiques en utilisant UNIQUEMENT l'équipement de gym disponible. Concentrez-vous sur la création de plans d'entraînement complets avec des exercices spécifiques, des séries, des répétitions et des périodes de repos.\n\nÉquipement de gym disponible:\n{equipment_info}\n\nLors de la création de routines d'entraînement:\n- Utilisez UNIQUEMENT l'équipement listé ci-dessus\n- Fournissez des séries, répétitions et périodes de repos spécifiques\n- Incluez un échauffement et une récupération appropriés\n- Considérez le niveau de forme et l'expérience de l'utilisateur\n- Rendez les routines pratiques pour les étudiants avec un temps limité\n- Expliquez la forme appropriée pour chaque exercice\n- Suggérez des plages de poids basées sur l'équipement disponible\n\nPour les splits d'entraînement hebdomadaires:\n- Planifiez chaque jour de la semaine (lundi-dimanche)\n- Incluez des jours de repos pour la récupération\n- Équilibrez les groupes musculaires tout au long de la semaine\n- Considérez la fréquence d'exercice de l'utilisateur\n- Fournissez des recommandations de progression\n- Incluez de la variété pour éviter l'ennui\n\nVous pouvez aussi fournir des conseils nutritionnels de base et des calculs de calories quand demandé. Répondez en français.",
        "Korean": f"당신은 MyGymBro의 학생용 AI 운동 계획자입니다. 당신의 주요 기능은 사용 가능한 짐 기구만을 사용하여 상세하고 실용적인 운동 루틴을 만드는 것입니다. 구체적인 운동, 세트, 반복 횟수, 휴식 시간이 포함된 완전한 운동 계획을 만드는 데 집중하세요.\n\n사용 가능한 짐 기구:\n{equipment_info}\n\n운동 루틴을 만들 때:\n- 위에 나열된 기구만 사용하세요\n- 구체적인 세트, 반복 횟수, 휴식 시간을 제공하세요\n- 적절한 워밍업과 쿨다운을 포함하세요\n- 사용자의 체력 수준과 경험을 고려하세요\n- 시간이 제한된 학생들에게 실용적인 루틴을 만드세요\n- 각 운동의 올바른 자세를 설명하세요\n- 사용 가능한 기구를 바탕으로 무게 범위를 제안하세요\n\n요청받을 때 기본적인 영양 조언과 칼로리 계산도 제공할 수 있습니다. 한국어로 답변해주세요.",
        "Mandarin": f"你是MyGymBro的学生AI健身计划制定者。你的主要功能是仅使用可用的健身房设备创建详细、实用的锻炼计划。专注于创建包含具体练习、组数、次数和休息时间的完整锻炼计划。\n\n可用健身房设备：\n{equipment_info}\n\n制定锻炼计划时：\n- 仅使用上述列出的设备\n- 提供具体的组数、次数和休息时间\n- 包括适当的热身和冷却\n- 考虑用户的健身水平和经验\n- 为时间有限的学生制定实用的计划\n- 解释每个练习的正确姿势\n- 根据可用设备建议重量范围\n\n被询问时也可以提供基本营养建议和卡路里计算。请用中文回答。",
        "Spanish": f"Eres el planificador de entrenamientos IA de MyGymBro para estudiantes. Tu FUNCIÓN PRINCIPAL es crear rutinas de entrenamiento detalladas y prácticas usando ÚNICAMENTE el equipamiento de gimnasio disponible. Enfócate en crear planes de entrenamiento completos con ejercicios específicos, series, repeticiones y períodos de descanso.\n\nEquipamiento de gimnasio disponible:\n{equipment_info}\n\nAl crear rutinas de entrenamiento:\n- Usa ÚNICAMENTE el equipamiento listado arriba\n- Proporciona series, repeticiones y períodos de descanso específicos\n- Incluye calentamiento y enfriamiento apropiados\n- Considera el nivel de fitness y experiencia del usuario\n- Haz rutinas prácticas para estudiantes con tiempo limitado\n- Explica la forma correcta para cada ejercicio\n- Sugiere rangos de peso basados en el equipamiento disponible\n\nTambién puedes proporcionar consejos nutricionales básicos y cálculos de calorías cuando se te pida. Responde en español."
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
    
    

# Main chat interface
# Personal Information Section
st.markdown("### 📝 Your Information")
st.markdown("Please provide your information for personalized recommendations:")

# Personal info inputs
col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox(get_text("gender"), ["Male", "Female"], key="main_gender")
    age = st.number_input(get_text("age"), min_value=10, max_value=100, value=20, key="main_age")
with col2:
    st.markdown("**Height:**")
    col_height1, col_height2 = st.columns(2)
    with col_height1:
        feet = st.number_input("Feet", min_value=3, max_value=8, value=5, key="main_feet")
    with col_height2:
        inches = st.number_input("Inches", min_value=0, max_value=11, value=9, key="main_inches")
    height = feet * 30.48 + inches * 2.54  # Convert to cm for calculation
    weight_lbs = st.number_input("Weight (lbs)", min_value=66, max_value=440, value=154, key="main_weight_lbs")
    weight = weight_lbs * 0.453592  # Convert to kg for calculation

lifestyle = st.selectbox(
    get_text("lifestyle"),
    ["Lying down 15+ hours", "Almost no movement at home", "Student or office worker", "Active", "Very active"],
    key="main_lifestyle"
)

col3, col4 = st.columns(2)
with col3:
    exercise_experience = st.selectbox(
        get_text("exercise_experience"),
        ["Beginner", "1-3 years", "3-5 years intermediate", "5+ years advanced", "10+ years expert"],
        key="main_experience"
    )
    exercise_frequency = st.selectbox(
        get_text("exercise_frequency"),
        ["None", "1x/week", "2x/week", "3x/week", "4x/week", "5x/week", "6x/week", "7x/week"],
        key="main_frequency"
    )
with col4:
    fitness_level = st.selectbox(
        get_text("fitness_level"),
        ["Very poor", "Poor", "Below average", "Average", "Above average", "Good", "Very good"],
        key="main_fitness"
    )

# Sports/Activities section
sports_activities = st.multiselect(
    get_text("sports"),
    [
        "Basketball", "Soccer", "Tennis", "Swimming", "Running", "Cycling", 
        "Volleyball", "Baseball", "Football", "Hockey", "Track & Field", 
        "Wrestling", "Boxing", "Martial Arts", "Dance", "Yoga", "Pilates",
        "Rock Climbing", "Gymnastics", "Lacrosse", "Rugby", "Golf", 
        "Badminton", "Table Tennis", "Skiing", "Snowboarding", "Surfing",
        "Rowing", "Erg", "None - Just gym workouts", "Other"
    ],
    key="main_sports",
    help="Select all sports or activities you participate in regularly"
)

st.markdown("---")

# Main workout plan generator
st.markdown("### 🏋️ Create Your Workout Plan")
st.markdown("Get a personalized workout routine based on your gym's available equipment:")

# Quick workout plan buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💪 Full Body Workout", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a full body workout routine for me using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on compound movements and include proper warm-up and cool-down."

with col2:
    if st.button("🔥 Upper Body Focus", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create an upper body focused workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include chest, back, shoulders, and arms exercises."

with col3:
    if st.button("🦵 Lower Body Focus", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a lower body focused workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include legs, glutes, and core exercises."

# Additional workout options
col4, col5, col6 = st.columns(3)

with col4:
    if st.button("📅 Full Weekly Split", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a complete weekly workout split for me using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Plan out each day of the week with specific exercises, sets, reps, and rest days. Make it a balanced program that targets all muscle groups throughout the week."

with col5:
    if st.button("⚡ Quick 30-min Workout", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a quick 30-minute workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Make it efficient and effective for busy students."

with col6:
    if st.button("🏃 Cardio + Strength", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a cardio and strength combined workout using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include both cardio and strength training elements."

# More workout options
col7, col8, col9 = st.columns(3)

with col7:
    if st.button("🎯 Beginner-Friendly", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a beginner-friendly workout routine using the available gym equipment. I'm a {age}-year-old {gender.lower()}, beginner fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on proper form and progression."

with col8:
    if st.button("💪 Push/Pull/Legs Split", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a push/pull/legs workout split using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Include push day (chest, shoulders, triceps), pull day (back, biceps), and legs day with proper rest between muscle groups."

with col9:
    if st.button("🔥 High Intensity Training", use_container_width=True):
        sports_info = f" and participate in {', '.join(sports_activities)}" if sports_activities else " and don't participate in any specific sports"
        st.session_state["pre_filled_question"] = f"Create a high intensity training (HIT) workout using the available gym equipment. I'm a {age}-year-old {gender.lower()}, {fitness_level.lower()} fitness level, exercise {exercise_frequency.lower()}{sports_info}. Focus on maximum effort with shorter rest periods and higher intensity."

# Calorie calculator option
st.markdown("---")
st.markdown("### 📊 Additional Tools")

col7, col8 = st.columns(2)

with col7:
    if st.button("🔥 Calculate my maintenance calories", use_container_width=True):
        st.session_state["show_calorie_calculation"] = True

with col8:
    if st.button("💬 Ask MyGymBro anything", use_container_width=True):
        st.session_state["pre_filled_question"] = "I have a question about my fitness routine or nutrition. Please help me with personalized advice based on my information."

# Calorie calculation using main page inputs
if st.session_state.get("show_calorie_calculation", False):
    # Calculate BMR using main page inputs
    bmr = calculate_bmr(gender, age, height, weight)
    
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
        st.write(message["content"])

# Show helpful message if there are messages
if st.session_state["messages"]:
    st.info("💡 You can keep asking follow-up questions! Ask for modifications, more details, or different workout variations.")

# Handle pre-filled questions
if "pre_filled_question" in st.session_state and st.session_state["pre_filled_question"]:
    user_input = st.session_state["pre_filled_question"]
    st.session_state["pre_filled_question"] = None  # Clear after use
else:
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
        
        # Force rerun to show the new messages and enable continuous chat
        st.rerun()
        
    except Exception as e:
        # Show a helpful message instead of error
        st.chat_message("assistant").write(get_text("error_message"))
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "assistant", "content": "Network connection issue - AI response unavailable."})
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