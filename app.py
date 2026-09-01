import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MindMentor AI",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# =========================================================
# SESSION STATE & THEME INITIALIZATION
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "messages" not in st.session_state:
    # Elite System Prompt enforcing strict math and markdown formatting
    st.session_state.messages = [SystemMessage(content="""You are "MindMentor", an elite AI tutor, academic guide, and empathetic personal advisor. 
Your goal is to provide clear, structured, and deeply insightful answers.

FORMATTING & MATH RULES (CRITICAL):
1. MATH: You MUST use standard LaTeX for all mathematics. 
   - Use `$` for inline math (e.g., $E=mc^2$). 
   - Use `$$` for block equations, and ALWAYS place `$$` on its own separate line.
   - NEVER use `\[`, `\]`, `\(`, or `\)`. Streamlit will not render them.
2. STRUCTURE: Use Markdown effectively. Use `###` for section headers, bullet points for lists, and bold text for key terms.
3. CODE: Use proper fenced code blocks with language identifiers (e.g., ```python).

TONE & CONTENT GUIDELINES:
1. Socratic Method: Guide the user to understanding. Explain the "why" and "how" before giving the final answer.
2. Clarity over complexity: Break down difficult concepts using analogies and real-world examples.
3. Empathy: For personal questions, be objective, non-judgmental, and supportive. Provide actionable frameworks.
4. Check for understanding: End academic explanations with a brief question or prompt to test their knowledge.
5. Be concise but thorough. Avoid robotic filler phrases.
""")]

# =========================================================
# DYNAMIC CSS (LIGHT & DARK MODE)
# =========================================================
theme = st.session_state.theme

if theme == "Dark":
    css_vars = """
        --bg-deep: #0F172A;
        --bg-card: #1E293B;
        --bg-sidebar: #0F172A;
        --accent: #3B82F6;
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
        --border: #334155;
        --code-bg: #0F172A;
    """
else:
    css_vars = """
        --bg-deep: #FFFFFF;
        --bg-card: #F8FAFC;
        --bg-sidebar: #F1F5F9;
        --accent: #2563EB;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --border: #E2E8F0;
        --code-bg: #F1F5F9;
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    {css_vars}
}}

html, body, [class*="stApp"] {{
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
}}

/* Typography */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    color: var(--text-main) !important;
}}
.stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--text-muted) !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
}}

/* Buttons */
.stButton > button {{
    background-color: transparent;
    border: 1px solid var(--border);
    color: var(--text-main);
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s ease;
    width: 100%;
}}
.stButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background-color: rgba(59, 130, 246, 0.05);
}}

/* Chat Input */
.stChatInput textarea {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}}
.stChatInput textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}}

/* Code blocks inside markdown */
.stMarkdown code {{
    background-color: var(--code-bg) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border);
    border-radius: 4px;
}}

/* Chat message seamless integration */
div[data-testid="stChatMessage"] {{
    background-color: transparent !important;
    border: none !important;
    padding: 1rem 0 !important;
}}

/* Perfect Math Styling - Ensures MathJax inherits theme colors */
.MathJax {{
    color: var(--text-main) !important;
    font-size: 1.05em !important;
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MATH FORMATTING HELPER
# =========================================================
def format_math(text):
    """Converts LLM LaTeX delimiters to Streamlit-compatible MathJax delimiters."""
    if not isinstance(text, str): return text
    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
    text = text.replace(r'\(', '$').replace(r'\)', '$')
    return text

# =========================================================
# AI SETUP
# =========================================================
load_dotenv()
api = os.getenv("MISTRAL_API_KEY")

if not api:
    st.error("🚫 **MISTRAL_API_KEY not found.** Add it to your `.env` file and restart.")
    st.stop()

model = ChatMistralAI(model="mistral-small-2506", mistral_api_key=api)

# =========================================================
# SIDEBAR CONTROL PANEL
# =========================================================
with st.sidebar:
    st.markdown("### MindMentor")
    
    # Theme Toggle
    st.session_state.theme = st.radio(
        "Theme", 
        ["Dark", "Light"], 
        horizontal=True,
        index=0 if st.session_state.theme == "Dark" else 1,
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("#### Quick Actions")
    
    if st.button("Explain a Concept"):
        st.session_state.messages.append(HumanMessage(content="I want to learn about a new concept. Ask me what it is, and then break it down for me simply using analogies."))
        st.rerun()

    if st.button("Build a Study Plan"):
        st.session_state.messages.append(HumanMessage(content="Help me create a structured study schedule. Ask me what I'm studying, my goals, and how much time I have available."))
        st.rerun()

    if st.button("Brainstorm Ideas"):
        st.session_state.messages.append(HumanMessage(content="I need to brainstorm. Ask me what topic or problem I am trying to figure out, and help me generate structured ideas."))
        st.rerun()

    st.divider()

    if st.button("Clear Chat History"):
        st.session_state.messages = [st.session_state.messages[0]] # Keep system prompt
        st.rerun()

    st.caption("Tip: Use `$` for inline math and `$$` for block equations.")

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """<div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2rem; font-weight: 700; margin: 0; color: var(--text-main);">MindMentor</h1>
        <p style="color: var(--text-muted); font-size: 1rem; margin-top: 0.5rem;">Elite tutoring & personal guidance.</p>
    </div>""", 
    unsafe_allow_html=True
)

# =========================================================
# CHAT FEED
# =========================================================
has_conversation = any(not isinstance(m, SystemMessage) for m in st.session_state.messages)

if not has_conversation:
    st.info("Ask a study question, request a breakdown of a complex topic, or share what's on your mind. You can also use the tools in the sidebar.")

for msg in st.session_state.messages:
    if isinstance(msg, SystemMessage): continue
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    
    with st.chat_message(role):
        st.markdown(format_math(msg.content))

# =========================================================
# CHAT INPUT + AI LOGIC (Frictionless)
# =========================================================
if prompt := st.chat_input("Ask a question or share your thoughts..."):
    if not prompt.strip():
        st.warning("Please enter a question or thought to continue.")
    else:
        # 1. Add and display user message
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 2. Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = model.invoke(st.session_state.messages)
                response = format_math(result.content)
                st.markdown(response)
                
        # 3. Add AI message to state (No st.rerun() needed here for a smoother UI)
        st.session_state.messages.append(AIMessage(content=response))
