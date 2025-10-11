import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title = "Hqnks AI"
)

#사용자 데이터 저장 폴더 경로 지정
DATA_DIR = Path("data") #폴더 생성
DATA_DIR.mkdir(exist_ok = True) #폴더가 없으면 생성

#사용자 정보 저장 JSON 파일 경로 정의
USER_PROFILE_PATH = DATA_DIR/"user_profiles.json"

#사용자 정보 저장 파일이 없을 경우 파일을 초기화(없으면 생성, 있으면 덮어 씌움)
def init_user_profiles():
    # JSON 파일이 없다면 => 초기화
    if not USER_PROFILE_PATH.exists():
        #파일을 쓰기 모드로 열고 저장 준비
        with open(USER_PROFILE_PATH, "w", encoding="utf-8") as f:
            # 구조 : { "users" : { }}
            json.dump({"users" : {}}, f, ensure_ascii=False, indent=4)

#사용자 정보 파일을 일기
def load_user_profiles():
    if USER_PROFILE_PATH.exists():
        with open(USER_PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    #파일이 없을 경우 빈 사용자 정보 파일 반환
    return {"users" : {}}

#사용자 정보 파일에 저장
def save_user_profile(user_id, profile_data):
    profiles = load_user_profiles()
    profiles["users"][user_id] = profile_data

    #파일에 모든 사용자 정보 저장
    with open(USER_PROFILE_PATH, "w", encoding='utf-8') as f:
        json.dump(profiles, f, ensure_ascii = False, indent = 4)

def main():
    st.title("Sign Up")

    with st.form("signup_form"):
        #폼 상단에 제목
        st.header("Create Your Account")

        #사용자로부터 입력받는 필드
        id = st.text_input("ID")
        pw = st.text_input("Password", type="password")
        confirm_pw = st.text_input("Confirm Password", type = "password")
        nationality = st.text_input("nationality")
        age = st.number_input("Age", min_value=0, max_value=130, step=1)
        language_level = st.selectbox(
            "please pick the language level",
            ["beginger", "intermidiate", "advenced"]
        )

        col1, col2 = st.columns(2)
        with col1:
            singup_submitted = st.form_submit_button("Sign Up")
        with col2:
            if st.form_submit_button("Back to Login"):
                st.swith_page("main.py")
        # sign up 버튼이 눌렸을 때, 회원 정보 저장
        if singup_submitted:
            #모든 값이 입력값으로 채워졌는지 확인
            if not all([id, pw, confirm_pw, nationality, age, language_level]):
                st.error("Please fill in all required fields.")
            elif pw != confirm_pw:
                st.error("Passwords do not match.")
            else:
                profiles = load_user_profiles()

                #이미 존재하는 ID인지 확인
                if id in profiles["users"]:
                    st.error("This ID is already taken.")
                else:
                    #사용자 정보(필드들)을 딕셔너리로 grouping
                    profile_data = {
                        "id" : id,
                        "pw" : pw,
                        "nationality" : nationality,
                        "age": age,
                        "language_level" : language_level
                    }
                    
                    #사용자 정보 저장
                    save_user_profile(id, profile_data)

                    #메인 페이지로 이동
                    st.switch_page("main.py")
            
# 스크립트를 실행할 메인함수 호출
if __name__ == "__main__":
    init_user_profiles()
    main()

