import streamlit as st
import os
import json
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
try:
    if not API_KEY and "OPENAI_API_KEY" in st.secrets:
        API_KEY = st.secrets["OPENAI_API_KEY"]
except: pass

# --- UI CONFIG ---
st.set_page_config(page_title="Nexus AI", page_icon="🌐", layout="centered")

# --- KAMAL KA FRONTEND (HTML/CSS Injection) ---
st.markdown(f"""
    <style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    
    * {{ font-family: 'Poppins', sans-serif; }}

    /* Background Animation */
    .stApp {{
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }}

    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Container Styling */
    .glass-card {{
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 30px;
        color: white;
        margin-bottom: 20px;
    }}

    .title-text {{
        font-size: 50px;
        font-weight: 800;
        text-align: center;
        color: white;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }}

    /* Custom Input & Button */
    .stTextInput>div>div>input {{
        border-radius: 50px;
        padding: 15px 25px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}

    .stButton>button {{
        background: #fff;
        color: #e73c7e !important;
        border-radius: 50px;
        font-weight: 700;
        text-transform: uppercase;
        border: none;
        transition: 0.3s;
        width: 100%;
        height: 50px;
    }}

    .stButton>button:hover {{
        background: #e73c7e;
        color: #fff !important;
        transform: scale(1.05);
    }}

    /* Progress Bar */
    .stProgress > div > div > div > div {{
        background-image: linear-gradient(to right, #ffffff, #23a6d5);
    }}

    hr {{ border: 0.5px solid rgba(255,255,255,0.2); }}
    
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'data' not in st.session_state: st.session_state.data = None
if 'step' not in st.session_state: st.session_state.step = 0
if 'score' not in st.session_state: st.session_state.score = 0

# --- BACKEND LOGIC ---
def get_nexus_response(topic, lang):
    if not API_KEY:
        st.error("API Key not found in Secrets!")
        return None
    
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=API_KEY)
    prompt = f"Topic: {topic}. Language: {lang}. Provide 3 learning modules with content and 1 MCQ each in JSON format: {{'modules': [{{'title': '...', 'content': '...', 'quiz': {{'q': '...', 'options': [], 'a': '...'}} }}]}}"
    
    try:
        resp = llm.invoke([SystemMessage(content="You are a JSON-only AI Tutor."), HumanMessage(content=prompt)])
        return json.loads(resp.content.replace("```json", "").replace("```", "").strip())
    except: return None

# --- UI RENDER ---
st.markdown("<h1 class='title-text'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white;'>Elevate Your Intelligence Autonomously</p>", unsafe_allow_html=True)

if st.session_state.data is None:
    # --- LANDING PAGE ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    topic = st.text_input("", placeholder="Kya seekhna chahte hain? (e.g. Space, Coding, History)")
    lang = st.selectbox("Language", ["English", "Urdu/Hindi", "Spanish", "Arabic"])
    
    if st.button("Initialize Masterclass 🚀"):
        if topic:
            with st.spinner("Agent is designing your future..."):
                res = get_nexus_response(topic, lang)
                if res:
                    st.session_state.data = res
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- LEARNING PAGE ---
    data = st.session_state.data['modules']
    idx = st.session_state.step
    
    if idx < len(data):
        mod = data[idx]
        st.progress((idx + 1) / len(data))
        
        # Module Content
        st.markdown(f"""
            <div class='glass-card'>
                <h4 style='color: #fff;'>MODULE {idx + 1}: {mod['level'] if 'level' in mod else 'Learning'}</h4>
                <h2 style='font-weight: 800;'>{mod['title']}</h2>
                <hr>
                <p style='font-size: 1.1rem;'>{mod['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Quiz Section
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write(f"❓ **Quiz:** {mod['quiz']['q']}")
        ans = st.radio("Choose Option:", mod['quiz']['options'], key=f"q_{idx}")
        
        if st.button("Next Module ➡️"):
            if ans == mod['quiz']['a']:
                st.session_state.score += 1
            st.session_state.step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # --- COMPLETION PAGE ---
        st.balloons()
        st.markdown(f"""
            <div class='glass-card' style='text-align:center;'>
                <h1 style='font-size: 60px;'>🏆</h1>
                <h2>MISSION ACCOMPLISHED</h2>
                <p>Aapne successfully ye topic master kar liya hai.</p>
                <h1 style='font-size: 80px;'>{int((st.session_state.score/len(data))*100)}%</h1>
                <p>Accuracy Score</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Master New Topic"):
            st.session_state.data = None
            st.session_state.step = 0
            st.session_state.score = 0
            st.rerun()

# Sidebar (Hidden for clean look, or use for reset)
with st.sidebar:
    st.title("Nexus Control")
    if st.button("Restart App"):
        st.session_state.data = None
        st.rerun()
