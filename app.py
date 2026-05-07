import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import json

# Load API Key
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="StudyMate AI Agent", page_icon="📚", layout="wide")

# Custom CSS for a beautiful UI
st.markdown("""
    <style>
    .main { background-color: #F5F7F9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4A90E2; color: white; border: none; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    .module-card { padding: 20px; border-radius: 15px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #4A90E2; }
    .quiz-card { padding: 20px; border-radius: 15px; background-color: #E3F2FD; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'topic_data' not in st.session_state:
    st.session_state.topic_data = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_done' not in st.session_state:
    st.session_state.quiz_done = False

# --- AI AGENT FUNCTIONS ---
def get_llm():
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if not api_key:
        st.warning("Please enter your API Key in the sidebar!")
        return None
    return ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

def generate_study_plan(topic):
    llm = get_llm()
    if not llm: return None
    
    prompt = f"""
    You are an expert Study Tutor. The user wants to learn about: {topic}.
    1. Divide this topic into 3 logical learning chunks (Easy, Medium, Hard).
    2. For each chunk, provide a detailed explanation in a mix of Urdu and English (Hinglish) so it's easy to understand.
    3. Generate 1 MCQ for each chunk to test the user.
    
    Format the output strictly as a JSON like this:
    {{
        "study_plan": "Daily schedule advice here",
        "chunks": [
            {{
                "level": "Easy",
                "title": "Basic Intro",
                "explanation": "Simple Urdu-English explanation",
                "quiz": {{"question": "Q here", "options": ["A", "B", "C"], "answer": "A"}}
            }},
            ... (total 3 chunks)
        ]
    }}
    """
    response = llm.invoke([SystemMessage(content="You are a helpful AI Tutor."), HumanMessage(content=prompt)])
    # Clean response and parse JSON
    try:
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🤖 StudyMate AI")
    st.info("Aapka personal AI tutor jo apke liye asaan notes aur quiz banata hai.")
    if st.button("Reset Session"):
        st.session_state.topic_data = None
        st.session_state.current_step = 0
        st.session_state.score = 0
        st.rerun()

# --- MAIN UI ---
st.title("📚 StudyMate AI Agent")

if st.session_state.topic_data is None:
    # LANDING PAGE
    with st.container():
        st.markdown("<div class='module-card'>", unsafe_allow_html=True)
        topic_input = st.text_input("Aap aaj kya parhna chahte hain?", placeholder="e.g. Photosynthesis, Blockchain, ya World War 2")
        if st.button("Start Learning 🚀"):
            if topic_input:
                with st.spinner("Agent curriculum tayyar kar raha hai..."):
                    data = generate_study_plan(topic_input)
                    if data:
                        st.session_state.topic_data = data
                        st.rerun()
                    else:
                        st.error("JSON Error: Try again.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # LEARNING DASHBOARD
    data = st.session_state.topic_data
    chunks = data['chunks']
    current_idx = st.session_state.current_step
    
    # Progress Bar
    progress = (current_idx / len(chunks))
    st.progress(progress)
    st.write(f"Step {current_idx + 1} of {len(chunks)}")

    if current_idx < len(chunks):
        chunk = chunks[current_idx]
        
        # Display Lesson
        st.markdown(f"<div class='module-card'>", unsafe_allow_html=True)
        st.subheader(f"Level: {chunk['level']} - {chunk['title']}")
        st.write(chunk['explanation'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Quiz Section
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown(f"**Test Your Knowledge:** {chunk['quiz']['question']}")
        user_choice = st.radio("Sahi jawab chunein:", chunk['quiz']['options'], key=f"quiz_{current_idx}")
        
        if st.button("Submit Answer"):
            if user_choice == chunk['quiz']['answer']:
                st.success("Sahi Jawab! 🌟")
                st.session_state.score += 1
            else:
                st.error(f"Ghalat jawab! Sahi tha: {chunk['quiz']['answer']}")
            
            # Move to next step
            st.session_state.current_step += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # FINAL REPORT & PROGRESS
        st.balloons()
        st.markdown("<div class='module-card'>", unsafe_allow_html=True)
        st.header("🏁 Mission Accomplished!")
        st.write(f"Aapne topic mukammal kar liya hai.")
        st.metric("Final Score", f"{st.session_state.score}/{len(chunks)}")
        
        st.subheader("📅 Your Daily Study Plan")
        st.info(data['study_plan'])
        
        # Weak areas logic
        if st.session_state.score < len(chunks):
            st.warning("⚠️ Weak Area Identified: Aapko is topic par thori aur practice ki zaroorat hai.")
        else:
            st.success("🏆 Excellent work! Aap is topic ke master ban gaye hain.")
        
        if st.button("Start New Topic"):
            st.session_state.topic_data = None
            st.session_state.current_step = 0
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
