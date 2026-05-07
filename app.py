import streamlit as st
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# --- PAGE SETUP ---
st.set_page_config(page_title="Nexus AI | Global Tutor", page_icon="🌐", layout="wide")

# Custom CSS for Premium International Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .stButton>button { background: #1A1A1A; color: white; border-radius: 8px; font-weight: 600; transition: 0.3s; border: none; }
    .stButton>button:hover { background: #404040; transform: translateY(-2px); }
    .card { padding: 30px; border-radius: 20px; background: white; border: 1px solid #E0E0E0; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .quiz-card { background: #F0F7FF; padding: 25px; border-radius: 15px; border-left: 6px solid #007BFF; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND: API KEY HANDLING ---
# Pehle environment check karega, phir secrets (Streamlit/HF ke liye)
API_KEY = os.getenv("OPENAI_API_KEY") or (st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else None)

# --- SESSION STATE ---
if 'data' not in st.session_state:
    st.session_state.data = None
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'score' not in st.session_state:
    st.session_state.score = 0

# --- AGENT CORE LOGIC ---
def nexus_agent(topic, language):
    if not API_KEY:
        st.error("System Error: API Key not configured in backend.")
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=API_KEY)
    
    prompt = f"""
    You are 'Nexus AI', a world-class autonomous tutor. The user wants to master: {topic}.
    Language of instruction: {language}.
    
    Tasks:
    1. Break down the topic into 3 modules: Beginner, Intermediate, Advanced.
    2. Provide a clear, high-quality explanation for each module.
    3. Create 1 challenging MCQ for each module.
    4. Provide a 7-day study schedule at the end.

    Strictly output in JSON format:
    {{
        "schedule": "...",
        "modules": [
            {{
                "level": "...",
                "title": "...",
                "content": "...",
                "quiz": {{"q": "...", "options": ["...", "...", "..."], "a": "..."}}
            }}
        ]
    }}
    """
    
    try:
        response = llm.invoke([SystemMessage(content=f"You are Nexus AI. Output only JSON in {language}."), HumanMessage(content=prompt)])
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        st.error("Server Busy. Please try again.")
        return None

# --- UI DISPLAY ---
st.title("🌐 Nexus AI Agent")
st.subheader("Your Autonomous Executive Learning Partner")

# Sidebar for Language Selection
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2941/2941509.png", width=100)
    st.title("Settings")
    selected_lang = st.selectbox("Instruction Language", ["English", "Urdu/Hindi", "Spanish", "French", "Arabic", "Chinese"])
    st.divider()
    if st.button("Clear Memory & Restart"):
        st.session_state.data = None
        st.session_state.step = 0
        st.session_state.score = 0
        st.rerun()

if st.session_state.data is None:
    # Landing UI
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    target_topic = st.text_input("What do you want to master today?", placeholder="e.g. Neural Networks, Stock Market, Ancient History...")
    if st.button("Initialize Agent 🚀"):
        if target_topic:
            with st.spinner("Nexus AI is architecting your curriculum..."):
                result = nexus_agent(target_topic, selected_lang)
                if result:
                    st.session_state.data = result
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # Learning Dashboard
    data = st.session_state.data
    modules = data['modules']
    current_idx = st.session_state.step

    if current_idx < len(modules):
        mod = modules[current_idx]
        
        # Header Info
        st.caption(f"Module {current_idx + 1} of {len(modules)} | {mod['level']} Level")
        st.progress((current_idx + 1) / len(modules))

        # Content Card
        st.markdown(f"<div class='card'><h2>{mod['title']}</h2><p style='font-size:18px;'>{mod['content']}</p></div>", unsafe_allow_html=True)
        
        # Quiz Section
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown(f"**Assessment:** {mod['quiz']['q']}")
        choice = st.radio("Choose the correct option:", mod['quiz']['options'], key=f"q_{current_idx}")
        
        if st.button("Verify & Continue"):
            if choice == mod['quiz']['a']:
                st.toast("Correct! Module Unlocked.", icon="✅")
                st.session_state.score += 1
            else:
                st.toast(f"Incorrect. The answer was {mod['quiz']['a']}", icon="❌")
            
            st.session_state.step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Final Report
        st.balloons()
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.header("🏆 Course Completed!")
        st.metric("Final Proficiency Score", f"{(st.session_state.score / len(modules)) * 100}%")
        
        st.subheader("🗓️ Personalized 7-Day Execution Plan")
        st.info(data['schedule'])
        
        if st.button("Master Another Topic"):
            st.session_state.data = None
            st.session_state.step = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
