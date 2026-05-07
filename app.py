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
        animation: fadeIn 1s ease-out;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
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

    /* Premium Input & Button */
    .stTextInput>div>div>input {{
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        height: 50px;
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
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.4);
    }}

    /* Custom Footer */
    .footer {{
        text-align: center;
        padding: 40px 0;
        color: rgba(255,255,255,0.4);
        font-size: 14px;
    }}
    .flag-icon {{ width: 22px; vertical-align: middle; margin-left: 8px; border-radius: 2px; }}

    /* Hide Streamlit Stuff */
    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'data' not in st.session_state: st.session_state.data = None
if 'step' not in st.session_state: st.session_state.step = 0
if 'user_answers' not in st.session_state: st.session_state.user_answers = []

# --- CORE ENGINE: NEXUS AI (Using Llama 3.3) ---
def nexus_ai_engine(topic):
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY is missing!")
        return None
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are 'Nexus AI', a professional educational agent. 
    Topic: {topic}. 
    Language: Strictly English.

    Tasks:
    1. Divide the topic into 3 modules (Beginner, Intermediate, Advanced).
    2. Write high-quality educational content for each.
    3. For each module, create one open-ended question (where user must type the answer).
    4. Provide the correct sample answer for each question.
    5. Create a detailed 7-day study planner for the user.

    Output STRICTLY in JSON:
    {{
        "planner": "...",
        "modules": [
            {{
                "level": "...",
                "title": "...",
                "content": "...",
                "quiz_q": "...",
                "sample_ans": "..."
            }}
        ]
    }}
    """
    
    try:
        response = llm.invoke([SystemMessage(content="You are Nexus AI. Respond ONLY in JSON."), HumanMessage(content=prompt)])
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_content)
    except Exception as e:
        st.error(f"Error connecting to Nexus Core: {e}")
        return None

# --- UI CONTENT ---

st.markdown("<h1 class='title-text'>NEXUS AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; margin-bottom:40px;'>Personalized Autonomous Education</p>", unsafe_allow_html=True)

if st.session_state.data is None:
    # --- LANDING PAGE ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("What would you like to master today?")
    topic_input = st.text_input("", placeholder="Enter any topic (e.g., Quantum Physics, Web Dev...)")
    
    if st.button("INITIALIZE MASTERCLASS 🚀"):
        if topic_input:
            with st.spinner("Nexus AI is architecting your curriculum..."):
                result = nexus_ai_engine(topic_input)
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
        
        # Content Card
        st.markdown(f"""
            <div class='glass-card'>
                <h4 style='color:#818cf8; margin-bottom:0;'>MODULE {idx+1} • {mod['level']}</h4>
                <h2 style='margin-top:0; font-weight:800;'>{mod['title']}</h2>
                <hr style='opacity:0.1; margin: 20px 0;'>
                <p style='font-size: 1.1rem; line-height: 1.8; color:#cbd5e1;'>{mod['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Subjective Quiz Card
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📝 Module Assessment")
        st.write(mod['quiz_q'])
        user_ans = st.text_input("Type your answer here:", key=f"ans_{idx}")
        
        if st.button("SUBMIT ANSWER & CONTINUE ➡️"):
            if user_ans:
                st.session_state.user_answers.append(user_ans)
                st.success(f"Assessment Recorded.")
                time.sleep(0.5)
                st.session_state.step += 1
                st.rerun()
            else:
                st.warning("Please type an answer before continuing.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # --- FINAL RESULTS & PLANNER ---
        st.balloons()
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:70px; margin-bottom:0;'>🏆</h1>", unsafe_allow_html=True)
        st.header("Mastery Goal Reached")
        st.write("You have successfully navigated through all modules.")
        
        st.divider()
        st.subheader("🗓️ Your 7-Day Personalized Study Planner")
        st.info(st.session_state.data['planner'])
        
        # Show comparison for user to self-grade
        with st.expander("Review Your Answers"):
            for i, m in enumerate(modules):
                st.write(f"**Q{i+1}:** {m['quiz_q']}")
                st.write(f"**Your Answer:** {st.session_state.user_answers[i]}")
                st.write(f"**Nexus Recommended Answer:** {m['sample_ans']}")
                st.write("---")

        if st.button("START NEW MASTERCLASS"):
            st.session_state.data = None
            st.session_state.step = 0
            st.session_state.user_answers = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
    <div class='footer'>
        Made with ❤️ by <b>Pakistan</b>
        <img src="https://upload.wikimedia.org/wikipedia/commons/3/32/Flag_of_Pakistan.svg" class="flag-icon">
        <br>Nexus AI Core v3.0 | Autonomous Global Tutor
    </div>
    """, unsafe_allow_html=True)
