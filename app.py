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
    st.session_state.messages = [SystemMessage(content="""You are "MindMentor", an elite AI tutor, academic guide, and empathetic personal advisor. 
Your goal is to provide clear, structured, and deeply insightful answers.

CRITICAL FORMATTING RULES (YOU MUST FOLLOW THESE EXACTLY):
1. MATHEMATICS:
   - Use `$` for inline math (e.g., $E=mc^2$).
   - Use `$$` on its own separate line for block equations.
   - NEVER wrap math in parentheses like `( \int x dx )` or `( x^2 )`. This breaks the UI.
   - NEVER use `\[`, `\]`, `\(`, or `\)`.
2. TABLES:
   - When presenting data in a grid, you MUST use standard Markdown table syntax with pipes `|` and hyphens `-`.
   - NEVER use tab-separated text or space-separated columns.
3. LISTS & HEADERS:
   - Use `-` or `*` for bullet points.
   - Use `###` for subheadings to break up long text. Use `**bold**` for key terms.

TONE & PEDAGOGY:
1. Socratic Method: Guide the user. Explain the "why" and "how".
2. Clarity: Use analogies. Break down complex steps.
3. Empathy: Be objective and supportive for personal questions.
4. Check for Understanding: End academic explanations with a brief prompt or question.
""")]

# =========================================================
# DYNAMIC CSS (LIGHT & DARK MODE + PREMIUM ASK BAR)
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
        --shadow-input: 0 8px 24px rgba(0, 0, 0, 0.4);
        --shadow-input-focus: 0 8px 30px rgba(59, 130, 246, 0.2);
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
        --shadow-input: 0 8px 24px rgba(0, 0, 0, 0.06);
        --shadow-input-focus: 0 8px 30px rgba(37, 99, 235, 0.12);
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
.stButton > button, .stDownloadButton > button {{
    background-color: transparent;
    border: 1px solid var(--border);
    color: var(--text-main);
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s ease;
    width: 100%;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background-color: rgba(59, 130, 246, 0.05);
}}

/* =========================================
   PREMIUM MINIMAL ASK BAR (CHAT INPUT)
   ========================================= */
/* Add a gradient mask so chat messages fade into the input area */
.stChatInput {{
    background: linear-gradient(to bottom, transparent, var(--bg-deep) 25%) !important;
    padding-top: 25px !important;
}}

/* The actual text area */
.stChatInput textarea {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important; /* Soft, modern curve */
    padding: 16px 24px !important;
    font-size: 1rem !important;
    line-height: 1.5 !important;
    box-shadow: var(--shadow-input) !important; /* Floating effect */
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}}

/* Focus state: Lift up and glow */
.stChatInput textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: var(--shadow-input-focus) !important;
    transform: translateY(-2px); /* Micro-interaction lift */
    background-color: var(--bg-deep) !important;
}}

/* Placeholder styling */
.stChatInput textarea::placeholder {{
    color: var(--text-muted) !important;
    font-weight: 300;
    opacity: 0.8;
}}

/* Code blocks */
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

/* Perfect Math Styling */
.MathJax {{
    color: var(--text-main) !important;
    font-size: 1.05em !important;
}}

/* PREMIUM MARKDOWN TABLES */
.stMarkdown table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.95rem;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
}}
.stMarkdown th {{
    background-color: var(--bg-card);
    color: var(--accent);
    font-weight: 600;
    text-align: left;
    padding: 12px 15px;
    border-bottom: 2px solid var(--accent);
}}
.stMarkdown td {{
    padding: 12px 15px;
    border-bottom: 1px solid var(--border);
    color: var(--text-main);
    background-color: var(--bg-deep);
}}
.stMarkdown tr:last-child td {{
    border-bottom: none;
}}
.stMarkdown tr:hover td {{
    background-color: rgba(59, 130, 246, 0.05);
}}

/* Minimalist scrollbar */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MATH & MARKDOWN CLEANER (The Safety Net)
# =========================================================
def clean_and_format(text):
    """Catches and fixes common LLM formatting mistakes before rendering."""
    if not isinstance(text, str): return text
    
    # 1. Fix standard LaTeX brackets that Streamlit hates
    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
    text = text.replace(r'\(', '$').replace(r'\)', '$')
    
    # 2. Fix the weird "( \mathcommand ... )" issue
    # Catches things like ( \int x dx ) and converts to $ \int x dx $
    text = re.sub(
        r'\(\s*(\\(?:int|sum|prod|lim|frac|sqrt|alpha|beta|gamma|theta|pi|infty|leq|geq|neq|approx|times|div|cdot|text|mathbf|mathrm).*?)\s*\)', 
        r'$\1$', 
        text
    )
    
    # 3. Clean up accidental double spaces or weird line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
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

    if st.button("Solve a Math Problem"):
        st.session_state.messages.append(HumanMessage(content="I have a math problem. Ask me to provide it, and then solve it step-by-step using proper LaTeX formatting."))
        st.rerun()

    st.divider()
    st.markdown("#### Export & Manage")
    
    # Export Notes Feature
    if len(st.session_state.messages) > 1:
        notes = "# MindMentor Study Notes\n\n"
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                notes += f"### ❓ Question\n{msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                notes += f"### 💡 Answer\n{msg.content}\n\n---\n\n"
        
        st.download_button(
            label="📥 Export Notes (.md)",
            data=notes,
            file_name="mindmentor_notes.md",
            mime="text/markdown",
            use_container_width=True
        )

    if st.button("Clear Chat History"):
        st.session_state.messages = [st.session_state.messages[0]] # Keep system prompt
        st.rerun()

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
        # Apply the cleaning function to all messages before rendering
        st.markdown(clean_and_format(msg.content))

# =========================================================
# CHAT INPUT + AI LOGIC
# =========================================================
# Updated placeholder text to be cleaner and more inviting
if prompt := st.chat_input("Ask anything... Math, Study Plans, Life Advice"):
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
                response = clean_and_format(result.content)
                st.markdown(response)
                
        # 3. Add AI message to state
        st.session_state.messages.append(AIMessage(content=response))
