import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_teddynote.prompts import load_prompt
load_dotenv()

#to run
# cd 00-MyProject
# poetry shell
# streamlit run main.py

st.write("# what's today's agenda?")


if "messages" not in st.session_state:
    st.session_state["messages"] = []

#adding side bar + history clearment

with st.sidebar:
    clear_btn = st.button("history clear")

    if clear_btn:
        st.session_state["messages"] = []
    
    selected_prompt = st.selectbox(
        "프롬포트 선택",
        ("기본모드", "SNS 게시글", "요약"),
        index = 1
    )
    #st.write(selected_prompt)


# 추가: create_chain() 함수 정의
def create_chain(prompt_type):
    # 추가: prompt_type 에 입력된 프롬프트에 따라 템플릿이 변경
    if prompt_type == "기본모드":
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "당신은 친절한 AI 어시스턴트입니다."),
                ("human", "Question:{question}")
            ]
        )
    
    if prompt_type == "SNS 게시글":
        prompt = load_prompt("prompts/sns.yaml", encoding = "utf-8")
    
    if prompt_type == "요약":
        pass



    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.4)

    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser
    return chain



def print_message():
    for chat_message in st.session_state['messages']:
        st.chat_message(chat_message.role).write(chat_message.content)

print_message()

def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))



user_input = st.chat_input("what do you need my nigga")

if user_input:
    st.chat_message("user").write(user_input)

    chain = create_chain(selected_prompt)
    ai_answer = chain.invoke({"question": user_input})

    st.chat_message("assistent").write(ai_answer)

    add_message("user", user_input)
    add_message("assistant", ai_answer)






