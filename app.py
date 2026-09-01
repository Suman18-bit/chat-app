import os
import re
import random
import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MindMentor AI",
    page_icon="🦉",
    layout="centered",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLING — Deep Focus / Academic Theme
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:wght@700&display=swap');

:root {
    --bg-deep: #0B1120;
    --bg-card: #151E2F;
    --bg-sidebar: #111827;
    --accent-blue: #3B82F6;
    --accent-purple: #8B5CF6;
    --text-main: #F3F4F6;
    --text-muted: #9CA3AF;
    --border: #1F2937;
}

html, body, [class*="st-"], [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-deep);
    color: var(--text-main);
}

.stApp {
    background: linear-gradient(135deg, #0B1120 0%, #111827 100%) !important;
}

/* Header */
.app-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.app-title {
    font-family: 'Merriweather', serif;
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.app-subtitle {
    color: var(--text-muted);
    font-size: 1.1rem;
    font-weight: 300;
    margin-top: 0.5rem;
}
.header-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
    margin: 1.5rem auto;
    width: 80%;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-main);
}
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: var(--text-main);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: var(--text-main);
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2));
    border-color: var(--accent-blue);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    color: #fff;
}

/* Chat Input */
.stChatInput textarea {
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
.stChatInput textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* Empty State */
.empty-state {
    text-align: center;
    color: var(--text-muted);
    background: var(--bg-card);
    border: 1px dashed var(--border);
    border-radius: 12px;
    padding: 40px 20px;
    margin-top: 20px;
}
.empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
.empty-state-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 0.5rem;
}

/* Metrics */
div[data-testid="stMetric"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px;
}

/* Chat message styling overrides for better blending */
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="app-header">', unsafe_allow_html=True)
st.markdown('<div class="app-title">MindMentor AI</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Your elite AI tutor for academic mastery and thoughtful personal guidance.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)

# =========================================================
# AI SETUP
# =========================================================
load_dotenv()
api = os.getenv("MISTRAL_API_KEY")

if not api:
    st.error("🚫 **MISTRAL_API_KEY not found.** Add it to your `.env` file and restart the app.")
    st.stop()

model = ChatMistralAI(model="mistral-small-2506", mistral_api_key=api)

# =========================================================
# SESSION STATE & ELITE SYSTEM PROMPT
# =========================================================
SYSTEM_PROMPT = """You are "MindMentor", an elite AI tutor, academic guide, and empathetic personal advisor. 
Your goal is to help users master complex subjects, organize their studies, and navigate personal challenges with clarity, wisdom, and encouragement.

GUIDELINES FOR ACADEMIC & STUDY QUESTIONS:
1. Structure & Clarity: Use bold headings, bullet points, and numbered lists to break down complex information. Never output walls of text.
2. The Socratic Method: Don't just give the final answer. Explain the "why" and "how". Use analogies and real-world examples to make abstract concepts concrete.
3. Check for Understanding: End your explanations with a brief, thought-provoking question or a mini-challenge to test their grasp of the concept.
4. Formatting: Use proper markdown code blocks for programming, and LaTeX formatting (e.g., $E=mc^2$) for mathematics and scientific formulas.

GUIDELINES FOR PERSONAL & LIFE QUESTIONS:
1. Empathy & Objectivity: Be deeply empathetic, non-judgmental, and objective. Validate their feelings before offering solutions.
2. Balanced Perspectives: When giving advice, weigh pros and cons. Help the user see multiple angles of a situation.
3. Actionable Frameworks: Provide step-by-step, practical frameworks for self-improvement, productivity, or problem-solving.
4. Tone: Maintain a supportive, encouraging, and professional tone. Act as a wise mentor, not a dictator.

GENERAL RULES:
- Adapt your vocabulary and depth to the user's apparent level of understanding.
- Be concise but thorough. Avoid unnecessary fluff.
- Never break character. You are a dedicated mentor.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

# =========================================================
# SIDEBAR CONTROL PANEL
# =========================================================
with st.sidebar:
    st.markdown("### 🧠 Study Hub")
    
    # Metrics
    interactions = sum(1 for m in st.session_state.messages if isinstance(m, AIMessage))
    st.metric("Topics Explored", interactions)

    st.divider()
    st.markdown("#### ⚡ Quick Actions")
    
    # Quick actions for study and personal growth
    if st.button("🧠 Explain a Concept", use_container_width=True):
        st.session_state.messages.append(HumanMessage(content="I want to learn about a new concept. Ask me what it is, and then break it down for me simply using analogies."))
        with st.spinner("Preparing explanation..."):
            result = model.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=result.content))
        st.rerun()

    if st.button("📅 Build a Study Plan", use_container_width=True):
        st.session_state.messages.append(HumanMessage(content="Help me create a structured study schedule. Ask me what I'm studying, my goals, and how much time I have available."))
        with st.spinner("Drafting schedule..."):
            result = model.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=result.content))
        st.rerun()

    if st.button("🧘 Personal Advice", use_container_width=True):
        st.session_state.messages.append(HumanMessage(content="I need some objective personal advice. Ask me what's on my mind and help me think through it."))
        with st.spinner("Reflecting..."):
            result = model.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=result.content))
        st.rerun()
        
    if st.button("📝 Summarize Text", use_container_width=True):
        st.session_state.messages.append(HumanMessage(content="I have some text or a topic I need summarized. Tell me to paste it or name the topic."))
        with st.spinner("Ready to summarize..."):
            result = model.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=result.content))
        st.rerun()

    st.divider()

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.toast("🧹 History cleared. Ready for a new topic!")
        st.rerun()

# =========================================================
# CHAT FEED (Native Streamlit Markdown Support)
# =========================================================
has_conversation = any(not isinstance(m, SystemMessage) for m in st.session_state.messages)

if not has_conversation:
    st.markdown(
        """<div class="empty-state">
            <div class="empty-state-icon">🎓</div>
            <div class="empty-state-title">Ready to learn and grow?</div>
            <p>Ask a study question, request a breakdown of a complex topic, or share what's on your mind. You can also use the tools in the sidebar.</p>
        </div>""",
        unsafe_allow_html=True,
    )

# Render chat history using native st.chat_message for rich markdown support (code, math, tables)
for msg in st.session_state.messages:
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    avatar = "🧑‍🎓" if role == "user" else "🦉"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg.content)

# =========================================================
# CHAT INPUT + AI LOGIC
# =========================================================
if prompt := st.chat_input("Ask a study question or share what's on your mind..."):
    if not prompt.strip():
        st.warning("Please enter a question or thought to continue.")
    else:
        # Add user message to state and display
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)
            
        # Generate and display AI response
        with st.chat_message("assistant", avatar="🦉"):
            spinners = ["Analyzing concepts...", "Structuring the answer...", "Reviewing data...", "Formulating advice..."]
            with st.spinner(random.choice(spinners)):
                result = model.invoke(st.session_state.messages)
                st.markdown(result.content)
                
        # Add AI message to state
        st.session_state.messages.append(AIMessage(content=result.content))
        
        # Rerun to clear the input box and update state cleanly
        st.rerun()
