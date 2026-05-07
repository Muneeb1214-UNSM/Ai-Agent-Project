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
st.set_page_config(page_title="Nexus AI | Autonomous Learning Executive", page_icon="🌐", layout="centered")

# --- PREMIUM ANIMATED UI (HTML/CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    * {{ font-family: 'Plus Jakarta Sans', sans-serif; }}

    /* Animated Background */
    .stApp {{
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a);
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
        background: rgba(255, 255, 255, 0.03);
        border-radius: 24px;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 35px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }}

    .title-text {{
        background: linear-gradient(to right, #818cf8, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 60px;
        font-weight: 800;
        text-align: center;
        letter-spacing: -2px;
    }}

    .stButton>button {{
        background: linear-gradient(90deg, #4f46e5, #3b82f6) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 55px;
        width: 100%;
        transition: 0.4s all ease;
    }}
    .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59, 130, 246, 0.4); }}

    .footer {{ text-align: center; padding: 40px 0; color: rgba(255,255,255,0.4); font-size: 14px; }}
    .flag-icon {{ width: 22px; vertical-align: middle; margin-left: 8px; border-radius: 2px; }}

    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'data' not in st.session_state: st.session_state.data = None
if 'step' not in st.session_state: st.session_state.step = 0
if 'user_answers' not in st.session_state: st.session_state.user_answers = []
if 'report' not in st.session_state: st.session_state.report = None

# --- CORE ENGINE: NEXUS AI AGENT ---
def nexus_ai_engine(topic):
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY is missing!")
        return None
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are 'Nexus AI', a professional educational agent. 
    Topic: {topic}. Language: Strictly English.
    Tasks:
    1. Divide the topic into 3 logical modules: Beginner, Intermediate, Advanced.
    2. Write content for each.
    3. Create one open-ended question for each module.
    4. Provide the correct sample answer for each question.
    5. Create a detailed 7-day study planner.

    Output STRICTLY in JSON format:
    {{
        "planner": "...",
        "modules": [
            {{ "level": "...", "title": "...", "content": "...", "quiz_q": "...", "sample_ans": "..." }}
        ]
    }}
    """
    try:
        response = llm.invoke([SystemMessage(content="You are Nexus AI. Respond ONLY in JSON."), HumanMessage(content=prompt)])
        return json.loads(response.content.replace("```json", "").replace("```", "").strip())
    except Exception as e:
        st.error(f"Error: {e}"); return None

# --- PERFORMANCE ANALYZER ---
def analyze_performance():
    if not GROQ_API_KEY: return None
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
    
    # Prepare comparison data
    comparison = []
    for i, mod in enumerate(st.session_state.data['modules']):
        comparison.append({
            "question": mod['quiz_q'],
            "user_answer": st.session_state.user_answers[i],
            "reference_answer": mod['sample_ans']
        })

    prompt = f"""
    Analyze the following user performance in a learning session.
    Data: {json.dumps(comparison)}
    
    Provide:
    1. A score from 0 to 100.
    2. A letter grade (A+, A, B, C, D, F).
    3. Constructive feedback (Strengths and areas for improvement).

    Output in JSON:
    {{ "score": 85, "grade": "A", "feedback": "..." }}
    """
    try:
        response = llm.invoke([SystemMessage(content="You are a Professor. Output JSON ONLY."), HumanMessage(content=prompt)])
        return json.loads(response.content.replace("```json", "").replace("```", "").strip())
    except: return None

# --- UI LOGIC ---
st.markdown("<h1 class='title-text'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; margin-bottom:40px;'>Autonomous Global Learning Agent</p>", unsafe_allow_html=True)

if st.session_state.data is None:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("What would you like to master today?")
    topic_input = st.text_input("", placeholder="Enter topic (e.g. Artificial Intelligence, Stock Market...)")
    if st.button("INITIALIZE MASTERCLASS 🚀"):
        if topic_input:
            with st.spinner("Nexus AI is architecting your curriculum..."):
                result = nexus_ai_engine(topic_input)
                if result:
                    st.session_state.data = result
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    modules = st.session_state.data['modules']
    idx = st.session_state.step
    
    if idx < len(modules):
        mod = modules[idx]
        st.progress((idx + 1) / len(modules))
        st.markdown(f"<div class='glass-card'><h4 style='color:#818cf8;'>MODULE {idx+1} • {mod['level']}</h4><h2 style='font-weight:800;'>{mod['title']}</h2><hr style='opacity:0.1;'><p style='font-size:1.1rem; line-height:1.8; color:#cbd5e1;'>{mod['content']}</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'><h3>📝 Module Assessment</h3>", unsafe_allow_html=True)
        st.write(mod['quiz_q'])
        user_ans = st.text_input("Your Answer:", key=f"ans_{idx}")
        if st.button("SUBMIT & CONTINUE ➡️"):
            if user_ans:
                st.session_state.user_answers.append(user_ans)
                st.session_state.step += 1
                st.rerun()
            else: st.warning("Please provide an answer.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # Final Step: Grade the Performance
        if st.session_state.report is None:
            with st.spinner("Nexus AI is analyzing your performance..."):
                st.session_state.report = analyze_performance()
                st.rerun()

        # --- FINAL ANALYTICS DASHBOARD ---
        st.balloons()
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.header("🏆 Performance Analytics")
        rep = st.session_state.report
        
        col1, col2 = st.columns(2)
        with col1: st.metric("Overall Score", f"{rep['score']}%")
        with col2: st.metric("Final Grade", rep['grade'])
        
        st.markdown("<div style='text-align:left; background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; margin-top:20px;'>", unsafe_allow_html=True)
        st.subheader("Professor's Feedback")
        st.write(rep['feedback'])
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("🗓️ 7-Day Study Execution Plan")
        st.info(st.session_state.data['planner'])
        
        with st.expander("Review My Answers"):
            for i, m in enumerate(modules):
                st.write(f"**Q{i+1}:** {m['quiz_q']}")
                st.write(f"**Your Answer:** {st.session_state.user_answers[i]}")
                st.write(f"**Nexus Recommended:** {m['sample_ans']}")
                st.write("---")

        if st.button("START NEW MASTERCLASS"):
            st.session_state.data = st.session_state.report = None
            st.session_state.step = st.session_state.score = 0
            st.session_state.user_answers = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='footer'>Made with ❤️ by <b>Pakistan</b><img src='https://upload.wikimedia.org/wikipedia/commons/3/32/Flag_of_Pakistan.svg' class='flag-icon'><br>Nexus AI Core v4.0 | Performance Analytics Enabled</div>", unsafe_allow_html=True)
