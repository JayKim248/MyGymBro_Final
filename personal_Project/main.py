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
        "ai_modes": "AI Modes",
        "basic_mode": "Basic Mode",
        "beginner_routine": "Beginner Routine",
        "time_based_routine": "Time-based Routine",
        "body_part_routine": "Body Part Routine",
        "equipment_guide": "Equipment Guide",
        "student_motivation": "Student Motivation",
        "student_profile": "Student Profile",
        "fitness_level": "Fitness Level",
        "available_time": "Available Time (minutes)",
        "save_profile": "Save Profile",
        "bmi_calculator": "BMI Calculator",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "calculate_bmi": "Calculate BMI",
        "equipment_management": "Equipment Management",
        "current_equipment": "Current Equipment List:",
        "routine_calculator": "Routine Set Calculator",
        "number_input": "Enter number (1 to n)",
        "calculate": "Calculate",
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
        "ai_modes": "Modes IA",
        "basic_mode": "Mode Basique",
        "beginner_routine": "Routine Débutant",
        "time_based_routine": "Routine par Temps",
        "body_part_routine": "Routine par Partie du Corps",
        "equipment_guide": "Guide d'Équipement",
        "student_motivation": "Motivation Étudiante",
        "student_profile": "Profil Étudiant",
        "fitness_level": "Niveau de Forme",
        "available_time": "Temps Disponible (minutes)",
        "save_profile": "Sauvegarder le Profil",
        "bmi_calculator": "Calculateur IMC",
        "height": "Taille (cm)",
        "weight": "Poids (kg)",
        "calculate_bmi": "Calculer l'IMC",
        "equipment_management": "Gestion d'Équipement",
        "current_equipment": "Liste d'Équipement Actuelle:",
        "routine_calculator": "Calculateur de Série de Routine",
        "number_input": "Entrez un nombre (1 à n)",
        "calculate": "Calculer",
        "chat_title": "💬 Discutez avec MyGymBro",
        "chat_placeholder": "💬 Posez des questions sur les routines de gym ou exercices!",
        "loading_message": "🤖 MyGymBro prépare une réponse...",
        "error_message": "Bonjour! Je suis MyGymBro. Actuellement il y a un problème de connexion réseau et je ne peux pas fournir de réponses IA. Veuillez réessayer plus tard. En attendant, essayez le calculateur IMC ou le calculateur de série de routine!",
        "footer": "💪 MyGymBro - Créateur de Routine de Gym pour Étudiants | Alimenté par OpenAI",
        "footer_subtitle": "Routines de gym parfaites pour étudiants, commencez avec MyGymBro!",
        "language": "Langue",
        "select_language": "Sélectionner la Langue"
    },
    "Korean": {
        "app_title": "MyGymBro - 학생용 짐 루틴 빌더",
        "welcome": "MyGymBro에 오신 것을 환영합니다! 💪",
        "subtitle": "학생들을 위한 AI 기반 짐 루틴 빌더",
        "ai_modes": "AI 모드",
        "basic_mode": "기본모드",
        "beginner_routine": "초보자 루틴",
        "time_based_routine": "시간별 루틴",
        "body_part_routine": "부위별 루틴",
        "equipment_guide": "기구 사용법",
        "student_motivation": "학생 동기부여",
        "student_profile": "학생 프로필",
        "fitness_level": "체력 수준",
        "available_time": "가능한 시간 (분)",
        "save_profile": "프로필 저장",
        "bmi_calculator": "BMI 계산기",
        "height": "키 (cm)",
        "weight": "몸무게 (kg)",
        "calculate_bmi": "BMI 계산",
        "equipment_management": "기구 관리",
        "current_equipment": "현재 기구 목록:",
        "routine_calculator": "루틴 세트 계산기",
        "number_input": "숫자 입력 (1부터 n까지)",
        "calculate": "계산하기",
        "chat_title": "💬 MyGymBro와 대화하기",
        "chat_placeholder": "💬 짐 루틴이나 운동에 대해 궁금한 것을 물어보세요!",
        "loading_message": "🤖 MyGymBro가 답변을 준비하고 있습니다...",
        "error_message": "안녕하세요! MyGymBro입니다. 현재 네트워크 연결에 문제가 있어 AI 응답을 받을 수 없습니다. 잠시 후 다시 시도해주세요. 그동안 BMI 계산기나 루틴 세트 계산기를 사용해보세요!",
        "footer": "💪 MyGymBro - Student Gym Routine Builder | Powered by OpenAI",
        "footer_subtitle": "학생들을 위한 완벽한 짐 루틴, MyGymBro와 함께 시작하세요!",
        "language": "언어",
        "select_language": "언어 선택"
    },
    "Mandarin": {
        "app_title": "MyGymBro - 学生健身计划构建器",
        "welcome": "欢迎使用MyGymBro！💪",
        "subtitle": "您的AI驱动学生健身计划构建器",
        "ai_modes": "AI模式",
        "basic_mode": "基础模式",
        "beginner_routine": "初学者计划",
        "time_based_routine": "时间计划",
        "body_part_routine": "部位计划",
        "equipment_guide": "器械指南",
        "student_motivation": "学生激励",
        "student_profile": "学生档案",
        "fitness_level": "健身水平",
        "available_time": "可用时间（分钟）",
        "save_profile": "保存档案",
        "bmi_calculator": "BMI计算器",
        "height": "身高（厘米）",
        "weight": "体重（公斤）",
        "calculate_bmi": "计算BMI",
        "equipment_management": "器械管理",
        "current_equipment": "当前器械列表：",
        "routine_calculator": "计划组计算器",
        "number_input": "输入数字（1到n）",
        "calculate": "计算",
        "chat_title": "💬 与MyGymBro聊天",
        "chat_placeholder": "💬 询问健身计划或运动相关问题！",
        "loading_message": "🤖 MyGymBro正在准备答案...",
        "error_message": "你好！我是MyGymBro。目前网络连接有问题，无法提供AI回复。请稍后再试。同时，可以试试BMI计算器或计划组计算器！",
        "footer": "💪 MyGymBro - 学生健身计划构建器 | 由OpenAI驱动",
        "footer_subtitle": "学生的完美健身计划，与MyGymBro一起开始！",
        "language": "语言",
        "select_language": "选择语言"
    },
    "Spanish": {
        "app_title": "MyGymBro - Constructor de Rutinas de Gimnasio para Estudiantes",
        "welcome": "¡Bienvenido a MyGymBro! 💪",
        "subtitle": "Tu constructor de rutinas de gimnasio con IA para estudiantes",
        "ai_modes": "Modos IA",
        "basic_mode": "Modo Básico",
        "beginner_routine": "Rutina Principiante",
        "time_based_routine": "Rutina por Tiempo",
        "body_part_routine": "Rutina por Parte del Cuerpo",
        "equipment_guide": "Guía de Equipos",
        "student_motivation": "Motivación Estudiantil",
        "student_profile": "Perfil de Estudiante",
        "fitness_level": "Nivel de Fitness",
        "available_time": "Tiempo Disponible (minutos)",
        "save_profile": "Guardar Perfil",
        "bmi_calculator": "Calculadora IMC",
        "height": "Altura (cm)",
        "weight": "Peso (kg)",
        "calculate_bmi": "Calcular IMC",
        "equipment_management": "Gestión de Equipos",
        "current_equipment": "Lista de Equipos Actual:",
        "routine_calculator": "Calculadora de Series de Rutina",
        "number_input": "Ingrese número (1 a n)",
        "calculate": "Calcular",
        "chat_title": "💬 Chatea con MyGymBro",
        "chat_placeholder": "💬 ¡Pregunta sobre rutinas de gimnasio o ejercicios!",
        "loading_message": "🤖 MyGymBro está preparando una respuesta...",
        "error_message": "¡Hola! Soy MyGymBro. Actualmente hay un problema de conexión de red y no puedo proporcionar respuestas de IA. Por favor, inténtalo de nuevo más tarde. Mientras tanto, ¡prueba la calculadora IMC o la calculadora de series de rutina!",
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
    
    # Language-specific prompts
    prompt_templates = {
        "English": {
            "Basic Mode": f"You are MyGymBro's student-exclusive AI gym routine builder. Create practical and sustainable gym routines that consider students' busy schedules, limited budgets, and various fitness levels.\n\nCurrent available equipment:\n{equipment_info}\n\nUse these equipment to create routines.",
            "Beginner Routine": f"You are a beginner gym routine expert for students. Provide step-by-step routines for students new to the gym, including basic exercises, appropriate weights, and safe form.\n\nCurrent available equipment:\n{equipment_info}\n\nSelect beginner-appropriate equipment from this list to create routines.",
            "Time-based Routine": f"You are a routine expert who understands students' time constraints. Provide efficient gym routines for various time slots like 30, 45, 60 minutes.\n\nCurrent available equipment:\n{equipment_info}\n\nCreate efficient routines that fit the time constraints.",
            "Body Part Routine": f"You are a specific body part focus routine expert. Provide routines targeting specific areas like chest, back, legs, shoulders, arms.\n\nCurrent available equipment:\n{equipment_info}\n\nUse these equipment to create body part focused routines.",
            "Equipment Guide": f"You are a gym equipment usage expert. Help students use various gym equipment correctly with step-by-step instructions without fear.\n\nCurrent available equipment:\n{equipment_info}\n\nExplain how to use these equipment.",
            "Student Motivation": "You are a fitness motivation expert for students. Encourage students who are tired from exam periods, assignments, part-time jobs, etc."
        },
        "French": {
            "Mode Basique": f"Vous êtes le constructeur de routines de gym IA exclusif aux étudiants de MyGymBro. Créez des routines de gym pratiques et durables qui tiennent compte des emplois du temps chargés des étudiants, des budgets limités et des différents niveaux de forme.\n\nÉquipement actuellement disponible:\n{equipment_info}\n\nUtilisez cet équipement pour créer des routines.",
            "Routine Débutant": f"Vous êtes un expert en routines de gym pour débutants étudiants. Fournissez des routines étape par étape pour les étudiants nouveaux au gym, incluant des exercices de base, des poids appropriés et une forme sûre.\n\nÉquipement actuellement disponible:\n{equipment_info}\n\nSélectionnez l'équipement approprié pour débutants de cette liste pour créer des routines.",
            "Routine par Temps": f"Vous êtes un expert en routines qui comprend les contraintes de temps des étudiants. Fournissez des routines de gym efficaces pour différents créneaux horaires comme 30, 45, 60 minutes.\n\nÉquipement actuellement disponible:\n{equipment_info}\n\nCréez des routines efficaces qui s'adaptent aux contraintes de temps.",
            "Routine par Partie du Corps": f"Vous êtes un expert en routines focalisées sur des parties spécifiques du corps. Fournissez des routines ciblant des zones spécifiques comme la poitrine, le dos, les jambes, les épaules, les bras.\n\nÉquipement actuellement disponible:\n{equipment_info}\n\nUtilisez cet équipement pour créer des routines focalisées sur des parties du corps.",
            "Guide d'Équipement": f"Vous êtes un expert en utilisation d'équipement de gym. Aidez les étudiants à utiliser correctement divers équipements de gym avec des instructions étape par étape sans crainte.\n\nÉquipement actuellement disponible:\n{equipment_info}\n\nExpliquez comment utiliser cet équipement.",
            "Motivation Étudiante": "Vous êtes un expert en motivation fitness pour étudiants. Encouragez les étudiants qui sont fatigués des périodes d'examens, devoirs, emplois à temps partiel, etc."
        },
        "Korean": {
            "기본모드": f"당신은 MyGymBro의 학생 전용 AI 짐 루틴 빌더입니다. 학생들의 바쁜 일정, 제한된 예산, 다양한 체력 수준을 고려하여 실용적이고 지속 가능한 짐 루틴을 만들어주세요.\n\n현재 사용 가능한 기구 목록:\n{equipment_info}\n\n이 기구들을 활용하여 루틴을 만들어주세요.",
            "초보자 루틴": f"당신은 학생들을 위한 초보자 짐 루틴 전문가입니다. 처음 짐에 오는 학생들을 위해 기본적인 운동법, 적절한 무게, 안전한 자세를 포함한 단계별 루틴을 제공해주세요.\n\n현재 사용 가능한 기구 목록:\n{equipment_info}\n\n이 기구들 중에서 초보자에게 적합한 것들을 선택하여 루틴을 만들어주세요.",
            "시간별 루틴": f"당신은 학생들의 시간 제약을 이해하는 루틴 전문가입니다. 30분, 45분, 60분 등 다양한 시간에 맞는 효율적인 짐 루틴을 제공해주세요.\n\n현재 사용 가능한 기구 목록:\n{equipment_info}\n\n시간에 맞게 효율적인 루틴을 만들어주세요.",
            "부위별 루틴": f"당신은 특정 부위 집중 루틴 전문가입니다. 가슴, 등, 하체, 어깨, 팔 등 특정 부위를 타겟으로 하는 루틴을 제공해주세요.\n\n현재 사용 가능한 기구 목록:\n{equipment_info}\n\n이 기구들을 활용하여 특정 부위에 집중한 루틴을 만들어주세요.",
            "기구 사용법": f"당신은 짐 기구 사용법 전문가입니다. 학생들이 겁내지 않고 다양한 짐 기구를 올바르게 사용할 수 있도록 단계별 설명을 알려주세요.\n\n현재 사용 가능한 기구 목록:\n{equipment_info}\n\n이 기구들에 대한 사용법을 설명해주세요.",
            "학생 동기부여": "당신은 학생들을 위한 피트니스 동기부여 전문가입니다. 시험 기간, 과제, 아르바이트 등으로 지친 학생들을 격려해주세요."
        },
        "Mandarin": {
            "基础模式": f"你是MyGymBro的学生专用AI健身计划构建器。创建实用且可持续的健身计划，考虑学生的繁忙日程、有限预算和不同的健身水平。\n\n当前可用器械：\n{equipment_info}\n\n使用这些器械创建计划。",
            "初学者计划": f"你是学生初学者健身计划专家。为刚来健身房的学生提供分步计划，包括基本练习、适当重量和安全姿势。\n\n当前可用器械：\n{equipment_info}\n\n从这些器械中选择适合初学者的来创建计划。",
            "时间计划": f"你是理解学生时间限制的计划专家。为30分钟、45分钟、60分钟等不同时间段提供高效的健身计划。\n\n当前可用器械：\n{equipment_info}\n\n创建符合时间限制的高效计划。",
            "部位计划": f"你是特定身体部位专注计划专家。提供针对胸部、背部、腿部、肩膀、手臂等特定部位的计划。\n\n当前可用器械：\n{equipment_info}\n\n使用这些器械创建身体部位专注的计划。",
            "器械指南": f"你是健身器械使用专家。帮助学生正确使用各种健身器械，提供分步说明而不让学生害怕。\n\n当前可用器械：\n{equipment_info}\n\n解释如何使用这些器械。",
            "学生激励": "你是学生健身激励专家。鼓励因考试期、作业、兼职工作等而疲惫的学生。"
        },
        "Spanish": {
            "Modo Básico": f"Eres el constructor de rutinas de gimnasio IA exclusivo para estudiantes de MyGymBro. Crea rutinas de gimnasio prácticas y sostenibles que consideren los horarios ocupados de los estudiantes, presupuestos limitados y varios niveles de fitness.\n\nEquipamiento actualmente disponible:\n{equipment_info}\n\nUsa este equipamiento para crear rutinas.",
            "Rutina Principiante": f"Eres un experto en rutinas de gimnasio para principiantes estudiantes. Proporciona rutinas paso a paso para estudiantes nuevos en el gimnasio, incluyendo ejercicios básicos, pesos apropiados y forma segura.\n\nEquipamiento actualmente disponible:\n{equipment_info}\n\nSelecciona equipamiento apropiado para principiantes de esta lista para crear rutinas.",
            "Rutina por Tiempo": f"Eres un experto en rutinas que entiende las limitaciones de tiempo de los estudiantes. Proporciona rutinas de gimnasio eficientes para varios horarios como 30, 45, 60 minutos.\n\nEquipamiento actualmente disponible:\n{equipment_info}\n\nCrea rutinas eficientes que se ajusten a las limitaciones de tiempo.",
            "Rutina por Parte del Cuerpo": f"Eres un experto en rutinas enfocadas en partes específicas del cuerpo. Proporciona rutinas dirigidas a áreas específicas como pecho, espalda, piernas, hombros, brazos.\n\nEquipamiento actualmente disponible:\n{equipment_info}\n\nUsa este equipamiento para crear rutinas enfocadas en partes del cuerpo.",
            "Guía de Equipos": f"Eres un experto en uso de equipamiento de gimnasio. Ayuda a los estudiantes a usar correctamente varios equipos de gimnasio con instrucciones paso a paso sin miedo.\n\nEquipamiento actualmente disponible:\n{equipment_info}\n\nExplica cómo usar este equipamiento.",
            "Motivación Estudiantil": "Eres un experto en motivación fitness para estudiantes. Anima a estudiantes que están cansados de períodos de exámenes, tareas, trabajos de medio tiempo, etc."
        }
    }
    
    # Get the appropriate prompt based on language and selected prompt
    current_language = st.session_state["language"]
    prompts = prompt_templates.get(current_language, prompt_templates["English"])
    system_prompt = prompts.get(prompt_type, prompts[list(prompts.keys())[0]])
    
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
    
    # Prompt selection
    prompt_options = {
        "English": ("Basic Mode", "Beginner Routine", "Time-based Routine", "Body Part Routine", "Equipment Guide", "Student Motivation"),
        "French": ("Mode Basique", "Routine Débutant", "Routine par Temps", "Routine par Partie du Corps", "Guide d'Équipement", "Motivation Étudiante"),
        "Korean": ("기본모드", "초보자 루틴", "시간별 루틴", "부위별 루틴", "기구 사용법", "학생 동기부여"),
        "Mandarin": ("基础模式", "初学者计划", "时间计划", "部位计划", "器械指南", "学生激励"),
        "Spanish": ("Modo Básico", "Rutina Principiante", "Rutina por Tiempo", "Rutina por Parte del Cuerpo", "Guía de Equipos", "Motivación Estudiantil")
    }
    
    selected_prompt = st.selectbox(
        f"🤖 {get_text('ai_modes')}",
        prompt_options[st.session_state["language"]],
        index=0
    )
    
    st.markdown("---")
    
    
    # Equipment Management
    st.markdown(f"### 🏋️‍♀️ {get_text('equipment_management')}")
    
    # Display current equipment
    equipment_df = load_gym_equipment()
    if equipment_df is not None:
        st.markdown(f"**{get_text('current_equipment')}**")
        # Clean up the dataframe for display
        display_df = equipment_df.copy()
        # Convert all columns to string to avoid display issues
        for col in display_df.columns:
            display_df[col] = display_df[col].astype(str)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info(f"📁 `data/GymMachineList.xlsx` {get_text('select_language').lower()}")
    
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