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