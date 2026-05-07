import streamlit as st
import os
import json
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# --- BACKEND: API SETUP ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
try:
    if not GROQ_API_KEY and "GROQ_API_KEY" in st.secrets:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    pass

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nexus AI Agent", page_icon="🌐", layout="centered")

# --- ADVANCED ANIMATED UI (HTML/CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    * {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    /* Animated Background Gradient */
    .stApp {{
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #581c87, #1e293b);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }}

    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Glassmorphism Card with Animation */
    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        border-radius: 24px;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 35px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        animation: fadeIn 1.5s ease-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .title-text {{
        background: linear-gradient(to right, #818cf8, #c084fc, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 60px;
        font-weight: 800;
        text-align: center;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }}

    /* Custom Input Styling */
    .stTextInput>div>div>input {{
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        transition: 0.3s;
    }}
    .stTextInput>div>div>input:focus {{
        border: 1px solid #818cf8 !important;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.4) !important;
    }}

    /* Premium Button */
    .stButton>button {{
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 55px;
        width: 100%;
        transition: 0.5s all ease;
    }}
    .stButton>button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(168, 85, 247, 0.4);
    }}

    /* Hide Streamlit Elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Custom Footer */
    .footer {{
        position: relative;
        text-align: center;
        padding: 50px 0 20px 0;
        color: rgba(255,255,255,0.4);
        font-size: 14px;
        font-weight: 400;
    }}
    .flag-icon {{
        width: 20px;
        vertical-align: middle;
        margin-left: 5px;
    }}

    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'data' not in st.session_state: st.session_state.data = None
if 'step' not in st.session_state: st.session_state.step = 0
if 'score' not in st.session_state: st.session_state.score = 0

# --- CORE ENGINE: NEXUS AI (Using Llama 3.3) ---
def nexus_ai_engine(topic, lang):
    if not GROQ_API_KEY:
        st.error("System Error: GROQ_API_KEY missing in Secrets.")
        return None
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are 'Nexus AI', a world-class autonomous tutor. 
    Topic: {topic}. Language: {lang}.

    1. Break into 3 modules: Beginner, Intermediate, Advanced.
    2. Write detailed content in Hinglish (Roman Urdu + English).
    3. 1 MCQ per module.
    4. 7-Day execution plan.

    Output STRICTLY in JSON format:
    {{
        "plan": "...",
        "modules": [
            {{
                "level": "...",
                "title": "...",
                "content": "...",
                "quiz": {{"q": "...", "options": ["a", "b", "c"], "a": "..."}}
            }}
        ]
    }}
    """
    
    try:
        response = llm.invoke([SystemMessage(content="You are Nexus AI. JSON ONLY."), HumanMessage(content=prompt)])
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        st.error(f"Agent Connectivity Issue: {e}")
        return None

# --- UI CONTENT ---

st.markdown("<h1 class='title-text'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; margin-bottom:40px; font-weight:300;'>Redefining Autonomous Education</p>", unsafe_allow_html=True)

if st.session_state.data is None:
    # --- LANDING PAGE ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("What do you want to master today?")
    topic_input = st.text_input("", placeholder="e.g. Quantum Physics, Web Development, Mughal Empire")
    selected_lang = st.selectbox("Choose Language", ["English", "Urdu/Hindi", "Spanish", "French"])
    
    if st.button("INITIALIZE NEURAL LINK 🚀"):
        if topic_input:
            with st.spinner("Nexus AI is architecting your curriculum..."):
                result = nexus_ai_engine(topic_input, selected_lang)
                if result:
                    st.session_state.data = result
                    st.rerun()
        else:
            st.warning("Please enter a topic.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- LEARNING DASHBOARD ---
    modules = st.session_state.data['modules']
    idx = st.session_state.step
    
    if idx < len(modules):
        mod = modules[idx]
        st.progress((idx + 1) / len(modules))
        
        st.markdown(f"""
            <div class='glass-card'>
                <h4 style='color:#818cf8; margin-bottom:0;'>MODULE {idx+1}</h4>
                <h2 style='margin-top:0; font-weight:800; color:white;'>{mod['title']}</h2>
                <hr style='opacity:0.1; margin: 20px 0;'>
                <p style='font-size: 1.15rem; line-height: 1.8; color:#cbd5e1;'>{mod['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Quick Assessment")
        st.write(mod['quiz']['q'])
        user_choice = st.radio("Choose the correct option:", mod['quiz']['options'], key=f"q_{idx}")
        
        if st.button("VERIFY & CONTINUE ➡️"):
            if user_choice == mod['quiz']['a']:
                st.session_state.score += 1
