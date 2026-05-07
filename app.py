import streamlit as st
import os
import json
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load Local .env if exists (for local testing)
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nexus AI | Global Learning Agent", page_icon="🌐", layout="wide")

# --- SAFE API KEY RETRIEVAL ---
API_KEY = os.getenv("OPENAI_API_KEY")

# Streamlit Cloud Secrets check
try:
    if not API_KEY and "OPENAI_API_KEY" in st.secrets:
        API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

# --- CUSTOM PREMIUM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    .main-card {
        padding: 2rem;
        border-radius: 1rem;
        background-color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #dee2e6;
        margin-bottom: 2rem;
    }

    .quiz-container {
        background-color: #f0f7ff;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 6px solid #007bff;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        height: 3rem;
        transition: all 0.3s ease;
    }

    .stProgress > div > div > div > div {
        background-color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'data' not in st.session_state:
    st.session_state.data = None
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'score' not in st.session_state:
    st.session_state.score = 0

# --- CORE AGENT LOGIC ---
def nexus_agent_engine(topic, language):
    if not API_KEY:
        st.error("❌ System Setup Incomplete: API Key not found in backend.")
        return None

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=API_KEY, temperature=0.7)
        
        prompt = f"""
        You are 'Nexus AI', a world-class autonomous tutor. The user wants to learn: {topic}.
        Language: {language}.
        
        Instructions:
        1. Split the topic into 3 logical modules (Beginner, Intermediate, Advanced).
        2. Provide high-quality content for each. Use a supportive tone.
        3. Create 1 MCQ for each module.
        4. Create a 7-day study plan.

        You MUST output ONLY valid JSON in the following structure:
        {{
            "study_plan": "text",
            "modules": [
                {{
                    "level": "text",
                    "title": "text",
                    "content": "text",
                    "quiz": {{"question": "text", "options": ["a", "b", "c"], "answer": "text"}}
                }}
            ]
        }}
        """
        
        response = llm.invoke([
            SystemMessage(content=f"You are a helpful JSON-only tutor. Always respond in {language}."),
            HumanMessage(content=prompt)
        ])
        
        # Clean JSON string
        json_data = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(json_data)
    except Exception as e:
        st.error(f"Agent is exhausted. Technical details: {str(e)}")
        return None

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2941/2941509.png", width=80)
    st.title("Nexus AI Settings")
    selected_lang = st.selectbox("Preferred Language", 
                                ["English", "Urdu/Hindi", "Spanish", "French", "Arabic", "Chinese"])
    
    st.divider()
    if st.button("🔄 Reset Global Agent"):
        st.session_state.data = None
        st.session_state.step = 0
        st.session_state.score = 0
        st.rerun()
    
    st.markdown("---")
    if not API_KEY:
        st.error("🔑 API Key Missing")
    else:
        st.success("🌐 Agent Online")

# --- MAIN INTERFACE ---
st.title("🌐 Nexus AI Learning Agent")
st.markdown("#### Your Autonomous Executive Learning Partner")

if st.session_state.data is None:
    # LANDING PAGE
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("What do you want to master today?")
    topic_input = st.text_input("Enter any topic, skill, or concept:", placeholder="e.g. Quantum Computing, Digital Marketing, ya Mughal History")
    
    if st.button("Initialize Learning 🚀"):
        if topic_input:
            with st.spinner("Nexus AI is architecting your curriculum..."):
                result = nexus_agent_engine(topic_input, selected_lang)
                if result:
                    st.session_state.data = result
                    st.rerun()
        else:
            st.warning("Please enter a topic to begin.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # LEARNING MODULES
    data = st.session_state.data
    modules = data['modules']
    current_idx = st.session_state.step

    if current_idx < len(modules):
        mod = modules[current_idx]
        
        # Progress Tracking
        progress_val = (current_idx) / len(modules)
        st.progress(progress_val)
        st.write(f"Module {current_idx + 1} of {len(modules)} | **{mod['level']} Level**")

        # Lesson Card
        st.markdown(f"""
            <div class='main-card'>
                <h2>{mod['title']}</h2>
                <hr>
                <p style='font-size: 1.1rem; line-height: 1.6;'>{mod['content']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quiz Section
        st.markdown("<div class='quiz-container'>", unsafe_allow_html=True)
        st.markdown(f"**Knowledge Check:** {mod['quiz']['question']}")
        user_ans = st.radio("Select the correct option:", mod['quiz']['options'], key=f"ans_{current_idx}")
        
        if st.button("Submit & Continue"):
            if user_ans == mod['quiz']['answer']:
                st.toast("Correct! Module Mastery Gained.", icon="✅")
                st.session_state.score += 1
            else:
                st.toast(f"Incorrect. The answer was: {mod['quiz']['answer']}", icon="❌")
            
            time.sleep(1) # Chota sa pause better UX ke liye
            st.session_state.step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # FINAL REPORT
        st.balloons()
        st.markdown("<div class='main-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.header("🏆 Course Successfully Completed!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Proficiency Score", f"{(st.session_state.score / len(modules)) * 100:.0f}%")
        with col2:
            st.metric("Modules Mastered", f"{st.session_state.score}/{len(modules)}")

        st.divider()
        st.subheader("🗓️ Your Personalized Study Execution Plan")
        st.info(data['schedule'])
        
        if st.button("Start New Masterclass"):
            st.session_state.data = None
            st.session_state.step = 0
            st.session_state.score = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<p style='text-align: center; color: #6c757d;'>Powered by Nexus AI Agent Core | Hackathon 2024</p>", unsafe_allow_html=True)
