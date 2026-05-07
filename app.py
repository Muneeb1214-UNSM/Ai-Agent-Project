import streamlit as st
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load API Key
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="StudyMate AI Agent", page_icon="📚", layout="wide")

# Custom CSS for UI
st.markdown("""
    <style>
    .main { background-color: #F5F7F9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4A90E2; color: white; border: none; }
    .module-card { padding: 20px; border-radius: 15px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #4A90E2; }
    .quiz-card { padding: 20px; border-radius: 15px; background-color: #E3F2FD; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'topic_data' not in st.session_state:
    st.session_state.topic_data = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'score' not in st.session_state:
    st.session_state.score = 0

# --- AI FUNCTIONS ---
def generate_study_plan(topic):
    # Sidebar se key uthana ya env se
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    
    if not api_key:
        st.error("Pehle Sidebar mein OpenAI API Key dalein!")
        return None

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
        
        prompt = f"""
        You are an expert Study Tutor. The user wants to learn about: {topic}.
        1. Divide this topic into 3 logical learning chunks (Easy, Medium, Hard).
        2. For each chunk, provide a detailed explanation in a mix of Urdu and English (Hinglish).
        3. Generate 1 MCQ for each chunk.
        
        Format the output strictly as a JSON:
        {{
            "study_plan": "Daily schedule advice",
            "chunks": [
                {{
                    "level": "Easy",
                    "title": "Basic Intro",
                    "explanation": "Explanation here",
                    "quiz": {{"question": "Q", "options": ["A", "B", "C"], "answer": "A"}}
                }}
            ]
        }}
        """
        
        messages = [
            SystemMessage(content="You are a helpful AI Tutor that outputs JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# --- UI LOGIC ---
st.title("📚 StudyMate AI Agent")

if st.session_state.topic_data is None:
    topic_input = st.text_input("Aap aaj kya parhna chahte hain?", placeholder="e.g. Artificial Intelligence, Photosynthesis...")
    if st.button("Start Learning 🚀"):
        if topic_input:
            with st.spinner("AI Agent parhai ka plan bana raha hai..."):
                data = generate_study_plan(topic_input)
                if data:
                    st.session_state.topic_data = data
                    st.rerun()
else:
    data = st.session_state.topic_data
    chunks = data['chunks']
    idx = st.session_state.current_step

    if idx < len(chunks):
        chunk = chunks[idx]
        st.markdown(f"<div class='module-card'><h3>{chunk['level']}: {chunk['title']}</h3><p>{chunk['explanation']}</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        ans = st.radio(chunk['quiz']['question'], chunk['quiz']['options'], key=f"q_{idx}")
        if st.button("Submit Answer"):
            if ans == chunk['quiz']['answer']:
                st.success("Sahi Jawab!")
                st.session_state.score += 1
            else:
                st.error(f"Ghalat! Sahi jawab tha: {chunk['quiz']['answer']}")
            st.session_state.current_step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.balloons()
        st.success(f"Mubarak ho! Score: {st.session_state.score}/{len(chunks)}")
        st.info(f"Daily Plan: {data['study_plan']}")
        if st.button("New Topic"):
            st.session_state.topic_data = None
            st.session_state.current_step = 0
            st.rerun()
