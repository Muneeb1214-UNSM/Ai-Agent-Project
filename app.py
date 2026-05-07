import streamlit as st
import os
import json
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# --- BACKEND: API SETUP ---
load_dotenv()
# Sabse pehle environment se key uthayega, phir Streamlit Secrets se
API_KEY = os.getenv("OPENAI_API_KEY")
try:
    if not API_KEY and "OPENAI_API_KEY" in st.secrets:
        API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    pass

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nexus AI Agent", page_icon="🌐", layout="centered")

# --- UI DESIGN: PREMIUM GLASSMORPHISM (HTML/CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    * {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    /* Animated Gradient Background */
    .stApp {{
        background: linear-gradient(-45deg, #0f172a, #1e293b, #334155, #1e1b4b);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }}

    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Glassmorphism Card */
    .glass-card {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }}

    .title-text {{
        background: linear-gradient(to right, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 55px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }}

    /* Customizing Streamlit Widgets to match UI */
    .stTextInput>div>div>input {{
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        height: 55px;
    }}

    .stButton>button {{
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
        height: 55px;
        transition: 0.4s ease;
    }}

    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
    }}

    .quiz-option {{
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
    }}

    /* Success Metric */
    [data-testid="stMetricValue"] {{ color: #4ade80 !important; font-size: 60px !important; }}

    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'data' not in st.session_state: st.session_state.data = None
if 'step' not in st.session_state: st.session_state.step = 0
if 'score' not in st.session_state: st.session_state.score = 0

# --- CORE ENGINE: NEXUS AI AGENT ---
def nexus_ai_engine(topic, lang):
    if not API_KEY:
        st.error("System Error: API Key missing from configuration.")
        return None
    
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=API_KEY)
    
    prompt = f"""
    You are 'Nexus AI', a world-class autonomous tutor. 
    User Topic: {topic}. 
    Instruction Language: {lang}.

    1. Break the topic into 3 logical modules: Beginner, Intermediate, Advanced.
    2. Write content in a mix of Urdu and English (Hinglish) for better understanding.
    3. Generate 1 MCQ per module.
    4. Provide a 7-day study plan at the end.

    Output STRICTLY in JSON:
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
        response = llm.invoke([SystemMessage(content="You are Nexus AI, an expert educational agent."), HumanMessage(content=prompt)])
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        st.error(f"Agent Connection Error: {e}")
        return None

# --- UI LOGIC ---

# Header
st.markdown("<h1 class='title-text'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; margin-bottom:40px;'>The Future of Autonomous Learning</p>", unsafe_allow_html=True)

if st.session_state.data is None:
    # --- LANDING VIEW ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("What do you want to learn today?")
    topic_input = st.text_input("", placeholder="e.g. Black Holes, Python Coding, ya History")
    selected_lang = st.selectbox("Preferred Language", ["English", "Urdu/Hindi", "Spanish", "Arabic"])
    
    if st.button("INITIALIZE MASTERCLASS 🚀"):
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
    # --- LEARNING VIEW ---
    modules = st.session_state.data['modules']
    idx = st.session_state.step
    
    if idx < len(modules):
        mod = modules[idx]
        
        # Progress Bar
        st.progress((idx + 1) / len(modules))
        st.write(f"Module {idx+1} of {len(modules)} | **{mod['level']}**")

        # Lesson Card
        st.markdown(f"""
            <div class='glass-card'>
                <h2 style='color:#60a5fa;'>{mod['title']}</h2>
                <hr style='opacity:0.2;'>
                <p style='font-size: 1.15rem; line-height: 1.7;'>{mod['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Quiz Section
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("⚡ Quick Assessment")
        st.write(mod['quiz']['q'])
        user_choice = st.radio("Choose the correct answer:", mod['quiz']['options'], key=f"q_{idx}")
        
        if st.button("VERIFY & NEXT MODULE ➡️"):
            if user_choice == mod['quiz']['a']:
                st.session_state.score += 1
                st.toast("Correct Answer!", icon="✅")
            else:
                st.toast(f"Incorrect. Correct was: {mod['quiz']['a']}", icon="❌")
            
            time.sleep(0.5)
            st.session_state.step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # --- FINAL RESULTS VIEW ---
        st.balloons()
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:80px;'>🎓</h1>", unsafe_allow_html=True)
        st.header("Mastery Achieved!")
        
        accuracy = int((st.session_state.score / len(modules)) * 100)
        st.metric("Proficiency Score", f"{accuracy}%")
        
        st.subheader("🗓️ 7-Day Execution Plan")
        st.info(st.session_state.data['plan'])
        
        if st.button("EXPLORE NEW TOPIC"):
            st.session_state.data = None
            st.session_state.step = 0
            st.session_state.score = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<p style='text-align:center; color:#475569; font-size:12px; margin-top:50px;'>Nexus AI Agent Core v1.0 | International Edition</p>", unsafe_allow_html=True)
