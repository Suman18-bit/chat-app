import os
import re
import time
import random
from datetime import datetime

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

if "accent_choice" not in st.session_state:
    st.session_state.accent_choice = "Blue"

if "meta" not in st.session_state:
    # Parallel store for timestamps, keyed by index in st.session_state.messages
    st.session_state.meta = {}

SYSTEM_PROMPT = """You are "MindMentor", an elite AI tutor, academic guide, and empathetic personal advisor.
Your goal is to provide clear, structured, and deeply insightful answers.

CRITICAL FORMATTING RULES (YOU MUST FOLLOW THESE EXACTLY):
1. MATHEMATICS:
   - Use `$` for inline math (e.g., $E=mc^2$).
   - Use `$$` on its own separate line for block equations.
   - NEVER wrap math in parentheses like `( \\int x dx )` or `( x^2 )`. This breaks the UI.
   - NEVER use `\\[`, `\\]`, `\\(`, or `\\)`.
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
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.meta[0] = {"time": datetime.now().strftime("%H:%M")}

# =========================================================
# ACCENT PALETTES
# =========================================================
ACCENTS = {
    "Blue":   {"main": "#3B82F6", "dim": "#2563EB", "glow": "rgba(59, 130, 246, 0.18)"},
    "Violet": {"main": "#8B5CF6", "dim": "#7C3AED", "glow": "rgba(139, 92, 246, 0.18)"},
    "Emerald":{"main": "#10B981", "dim": "#059669", "glow": "rgba(16, 185, 129, 0.18)"},
    "Amber":  {"main": "#F59E0B", "dim": "#D97706", "glow": "rgba(245, 158, 11, 0.18)"},
    "Rose":   {"main": "#F43F5E", "dim": "#E11D48", "glow": "rgba(244, 63, 94, 0.18)"},
}

accent = ACCENTS[st.session_state.accent_choice]

# =========================================================
# DYNAMIC CSS (LIGHT & DARK MODE + PREMIUM UI)
# =========================================================
theme = st.session_state.theme

if theme == "Dark":
    css_vars = f"""
        --bg-deep: #0B1120;
        --bg-card: #151F32;
        --bg-card-2: #1B2740;
        --bg-sidebar: #0B1120;
        --accent: {accent['main']};
        --accent-dim: {accent['dim']};
        --accent-glow: {accent['glow']};
        --text-main: #F8FAFC;
        --text-muted: #94A3B8;
        --text-faint: #5B6B85;
        --border: #26324A;
        --border-soft: #1C2740;
        --code-bg: #0B1120;
        --user-bubble: #1B2740;
        --assistant-bubble: transparent;
        --shadow-input: 0 10px 30px rgba(0, 0, 0, 0.45);
        --shadow-input-focus: 0 10px 36px var(--accent-glow);
        --shadow-card: 0 4px 18px rgba(0, 0, 0, 0.28);
        --success: #10B981;
        --danger: #F87171;
    """
else:
    css_vars = f"""
        --bg-deep: #FFFFFF;
        --bg-card: #F8FAFC;
        --bg-card-2: #F1F5F9;
        --bg-sidebar: #F6F8FB;
        --accent: {accent['main']};
        --accent-dim: {accent['dim']};
        --accent-glow: {accent['glow']};
        --text-main: #0F172A;
        --text-muted: #64748B;
        --text-faint: #A0AEC0;
        --border: #E2E8F0;
        --border-soft: #EDF1F7;
        --code-bg: #F1F5F9;
        --user-bubble: #EEF2FF;
        --assistant-bubble: transparent;
        --shadow-input: 0 10px 26px rgba(15, 23, 42, 0.08);
        --shadow-input-focus: 0 10px 30px var(--accent-glow);
        --shadow-card: 0 2px 12px rgba(15, 23, 42, 0.05);
        --success: #059669;
        --danger: #DC2626;
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Lora:ital,wght@0,500;1,500&display=swap');

:root {{
    {css_vars}
}}

* {{
    scroll-behavior: smooth;
}}

html, body, [class*="stApp"] {{
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
}}

/* Subtle ambient background glow */
[data-testid="stAppViewContainer"] {{
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, var(--accent-glow), transparent),
        radial-gradient(ellipse 60% 40% at 100% 0%, var(--accent-glow), transparent);
    background-repeat: no-repeat;
}}

/* Hide default Streamlit chrome */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{ background: transparent; }}

/* Typography */
.stMarkdown, .stMarkdown p, .stMarkdown li {{
    color: var(--text-main) !important;
    line-height: 1.7;
}}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    color: var(--text-main) !important;
    font-weight: 700 !important;
}}
.stMarkdown h3 {{
    font-size: 1.08rem !important;
    margin-top: 1.2rem !important;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--border-soft);
}}
.stMarkdown strong {{ color: var(--accent); font-weight: 600; }}
.stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--text-muted) !important;
}}

/* =========================================
   SIDEBAR
   ========================================= */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-soft);
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 1.2rem;
}}

.brand-block {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.2rem 0 1rem 0;
}}
.brand-icon {{
    width: 38px; height: 38px;
    border-radius: 11px;
    background: linear-gradient(135deg, var(--accent), var(--accent-dim));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem;
    box-shadow: 0 4px 14px var(--accent-glow);
    flex-shrink: 0;
}}
.brand-text h2 {{
    margin: 0; font-size: 1.15rem; font-weight: 800; color: var(--text-main);
    letter-spacing: -0.02em;
}}
.brand-text span {{
    font-size: 0.72rem; color: var(--text-muted); font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.06em;
}}

.section-label {{
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-faint);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.1rem 0 0.5rem 0;
}}

.stat-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 500;
}}
.stat-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
}}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-soft);
    color: var(--text-main);
    border-radius: 10px;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 0.55rem 0.8rem;
    transition: all 0.18s ease;
    width: 100%;
    box-shadow: var(--shadow-card);
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background-color: var(--accent-glow);
    transform: translateY(-1px);
}}
.stButton > button:active {{
    transform: translateY(0px);
}}
.stButton > button p {{ text-align: left !important; }}

/* Primary CTA style for the clear-chat button */
div[data-testid="stSidebar"] .stButton:last-of-type > button {{
    border-color: var(--danger);
    color: var(--danger);
}}
div[data-testid="stSidebar"] .stButton:last-of-type > button:hover {{
    background-color: rgba(248, 113, 113, 0.08);
}}

/* Radio pills for theme */
div[role="radiogroup"] {{
    gap: 6px;
}}
div[role="radiogroup"] label {{
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    padding: 4px 12px !important;
    border-radius: 8px !important;
    transition: all 0.15s ease;
}}
div[role="radiogroup"] label:hover {{
    border-color: var(--accent);
}}

/* Segmented accent swatches */
.accent-row {{ display: flex; gap: 8px; margin: 0.3rem 0 0.2rem 0; }}

/* =========================================
   HERO HEADER
   ========================================= */
.hero-wrap {{
    text-align: center;
    padding: 1.4rem 0 1.8rem 0;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-glow);
    color: var(--accent);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 5px 13px;
    border-radius: 999px;
    margin-bottom: 0.9rem;
    border: 1px solid var(--accent-glow);
}}
.hero-title {{
    font-size: 2.15rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, var(--text-main) 40%, var(--accent) 120%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.hero-sub {{
    color: var(--text-muted);
    font-size: 0.98rem;
    margin-top: 0.55rem;
    font-weight: 400;
}}

/* =========================================
   EMPTY STATE
   ========================================= */
.empty-state {{
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 16px;
    padding: 1.6rem 1.5rem;
    text-align: center;
    box-shadow: var(--shadow-card);
    margin-bottom: 1rem;
}}
.empty-state-icon {{
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
}}
.empty-state p {{
    color: var(--text-muted);
    font-size: 0.92rem;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.6;
}}
.suggestion-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 1.1rem;
}}
.suggestion-chip {{
    background: var(--bg-card-2);
    border: 1px solid var(--border-soft);
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 0.8rem;
    color: var(--text-main);
    text-align: left;
    font-weight: 500;
}}

/* =========================================
   CHAT MESSAGES
   ========================================= */
div[data-testid="stChatMessage"] {{
    background-color: transparent !important;
    border: none !important;
    padding: 0.85rem 0 !important;
    animation: fadeSlideIn 0.35s ease;
}}
@keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Avatar circles */
div[data-testid="stChatMessageAvatarUser"] {{
    background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
    box-shadow: 0 3px 10px var(--accent-glow);
}}
div[data-testid="stChatMessageAvatarAssistant"] {{
    background: var(--bg-card-2) !important;
    border: 1px solid var(--border-soft);
}}

/* User message gets a soft bubble via markdown container */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stMarkdown {{
    background: var(--user-bubble);
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1.05rem;
    display: inline-block;
}}

.msg-timestamp {{
    font-size: 0.68rem;
    color: var(--text-faint);
    margin-top: 4px;
    font-weight: 500;
    letter-spacing: 0.02em;
}}

/* Code blocks */
.stMarkdown code {{
    background-color: var(--code-bg) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border-soft);
    border-radius: 5px;
    padding: 1px 5px;
    font-size: 0.88em;
}}
.stMarkdown pre {{
    background-color: var(--code-bg) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-card);
}}
.stMarkdown pre code {{
    border: none;
    padding: 0;
}}

/* Perfect Math Styling */
.MathJax {{
    color: var(--text-main) !important;
    font-size: 1.05em !important;
}}

/* PREMIUM MARKDOWN TABLES */
.stMarkdown table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 1.4rem 0;
    font-size: 0.92rem;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border-soft);
    box-shadow: var(--shadow-card);
}}
.stMarkdown th {{
    background-color: var(--bg-card-2);
    color: var(--accent);
    font-weight: 700;
    text-align: left;
    padding: 11px 15px;
    border-bottom: 2px solid var(--accent);
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.stMarkdown td {{
    padding: 11px 15px;
    border-bottom: 1px solid var(--border-soft);
    color: var(--text-main);
    background-color: var(--bg-card);
}}
.stMarkdown tr:last-child td {{ border-bottom: none; }}
.stMarkdown tr:hover td {{ background-color: var(--accent-glow); }}

/* Blockquotes */
.stMarkdown blockquote {{
    border-left: 3px solid var(--accent);
    background: var(--bg-card);
    padding: 0.6rem 1rem;
    border-radius: 0 8px 8px 0;
    color: var(--text-muted) !important;
    margin: 1rem 0;
}}

/* =========================================
   PREMIUM MINIMAL ASK BAR (CHAT INPUT)
   ========================================= */
.stChatInput {{
    background: linear-gradient(to bottom, transparent, var(--bg-deep) 30%) !important;
    padding-top: 28px !important;
}}
.stChatInput textarea {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 22px !important;
    padding: 16px 24px !important;
    font-size: 0.98rem !important;
    line-height: 1.5 !important;
    box-shadow: var(--shadow-input) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}}
.stChatInput textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: var(--shadow-input-focus) !important;
    transform: translateY(-2px);
    background-color: var(--bg-deep) !important;
}}
.stChatInput textarea::placeholder {{
    color: var(--text-muted) !important;
    font-weight: 300;
    opacity: 0.85;
}}
.stChatInput button {{
    color: var(--accent) !important;
}}

/* Divider */
hr, [data-testid="stDivider"] {{
    border-color: var(--border-soft) !important;
    margin: 1rem 0 !important;
}}

/* Alerts */
.stAlert {{
    border-radius: 12px !important;
    border: 1px solid var(--border-soft) !important;
    box-shadow: var(--shadow-card);
}}

/* Spinner text */
.stSpinner > div {{
    text-align: left;
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
    if not isinstance(text, str):
        return text

    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
    text = text.replace(r'\(', '$').replace(r'\)', '$')

    text = re.sub(
        r'\(\s*(\\(?:int|sum|prod|lim|frac|sqrt|alpha|beta|gamma|theta|pi|infty|leq|geq|neq|approx|times|div|cdot|text|mathbf|mathrm).*?)\s*\)',
        r'$\1$',
        text
    )

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
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">🧠</div>
        <div class="brand-text">
            <h2>MindMentor</h2>
            <span>AI Study Companion</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    n_exchanges = sum(1 for m in st.session_state.messages if isinstance(m, HumanMessage))
    st.markdown(f"""
    <div class="stat-pill"><span class="stat-dot"></span> {n_exchanges} question{'s' if n_exchanges != 1 else ''} this session</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Appearance</div>', unsafe_allow_html=True)

    st.session_state.theme = st.radio(
        "Theme",
        ["Dark", "Light"],
        horizontal=True,
        index=0 if st.session_state.theme == "Dark" else 1,
        label_visibility="collapsed"
    )

    accent_names = list(ACCENTS.keys())
    st.session_state.accent_choice = st.selectbox(
        "Accent color",
        accent_names,
        index=accent_names.index(st.session_state.accent_choice),
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">Quick Actions</div>', unsafe_allow_html=True)

    def _add_prompt(text):
        st.session_state.messages.append(HumanMessage(content=text))
        st.session_state.meta[len(st.session_state.messages) - 1] = {"time": datetime.now().strftime("%H:%M")}

    if st.button("💡 Explain a Concept", use_container_width=True):
        _add_prompt("I want to learn about a new concept. Ask me what it is, and then break it down for me simply using analogies.")
        st.rerun()

    if st.button("🗓️ Build a Study Plan", use_container_width=True):
        _add_prompt("Help me create a structured study schedule. Ask me what I'm studying, my goals, and how much time I have available.")
        st.rerun()

    if st.button("📐 Solve a Math Problem", use_container_width=True):
        _add_prompt("I have a math problem. Ask me to provide it, and then solve it step-by-step using proper LaTeX formatting.")
        st.rerun()

    if st.button("🎯 Quiz Me", use_container_width=True):
        _add_prompt("Quiz me on a topic of my choice. Ask me what subject first, then ask one question at a time and check my answers.")
        st.rerun()

    st.markdown('<div class="section-label">Export & Manage</div>', unsafe_allow_html=True)

    if len(st.session_state.messages) > 1:
        notes = f"# MindMentor Study Notes\n_Exported {datetime.now().strftime('%B %d, %Y at %H:%M')}_\n\n---\n\n"
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                notes += f"### ❓ Question\n{msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                notes += f"### 💡 Answer\n{msg.content}\n\n---\n\n"

        st.download_button(
            label="📥 Export Notes (.md)",
            data=notes,
            file_name=f"mindmentor_notes_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.button("📥 Export Notes (.md)", disabled=True, use_container_width=True)

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.meta = {0: {"time": datetime.now().strftime("%H:%M")}}
        st.rerun()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.caption("Powered by Mistral Small · Built with LangChain")

# =========================================================
# HERO HEADER
# =========================================================
st.markdown(
    """<div class="hero-wrap">
        <div class="hero-badge">🧠 Elite AI Tutoring</div>
        <h1 class="hero-title">MindMentor</h1>
        <p class="hero-sub">Structured explanations, step-by-step math, and honest guidance — all in one place.</p>
    </div>""",
    unsafe_allow_html=True
)

# =========================================================
# CHAT FEED
# =========================================================
has_conversation = any(not isinstance(m, SystemMessage) for m in st.session_state.messages)

if not has_conversation:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">✨</div>
        <p><strong>Ready when you are.</strong><br>Ask a study question, request a concept breakdown, or just think out loud. Try one of these to get started:</p>
        <div class="suggestion-grid">
            <div class="suggestion-chip">📊 "Explain gradient descent simply"</div>
            <div class="suggestion-chip">📐 "Solve: ∫x²e^x dx"</div>
            <div class="suggestion-chip">🗓️ "Plan my exam week"</div>
            <div class="suggestion-chip">💬 "I'm stressed about finals"</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

for idx, msg in enumerate(st.session_state.messages):
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    avatar = "🧑" if role == "user" else "🧠"

    with st.chat_message(role, avatar=avatar):
        st.markdown(clean_and_format(msg.content))
        ts = st.session_state.meta.get(idx, {}).get("time")
        if ts:
            align = "right" if role == "user" else "left"
            st.markdown(f"<div class='msg-timestamp' style='text-align:{align};'>{ts}</div>", unsafe_allow_html=True)

# =========================================================
# CHAT INPUT + AI LOGIC
# =========================================================
if prompt := st.chat_input("Ask anything... Math, Study Plans, Life Advice"):
    if not prompt.strip():
        st.warning("Please enter a question or thought to continue.")
    else:
        # 1. Add and display user message
        st.session_state.messages.append(HumanMessage(content=prompt))
        user_idx = len(st.session_state.messages) - 1
        st.session_state.meta[user_idx] = {"time": datetime.now().strftime("%H:%M")}

        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
            st.markdown(f"<div class='msg-timestamp' style='text-align:right;'>{st.session_state.meta[user_idx]['time']}</div>", unsafe_allow_html=True)

        # 2. Generate and display AI response
        with st.chat_message("assistant", avatar="🧠"):
            thinking_labels = [
                "Thinking it through...",
                "Structuring the answer...",
                "Working through the logic...",
                "Connecting the dots...",
            ]
            with st.spinner(random.choice(thinking_labels)):
                try:
                    result = model.invoke(st.session_state.messages)
                    response = clean_and_format(result.content)
                except Exception as e:
                    response = (
                        "⚠️ **Something went wrong reaching the model.**\n\n"
                        f"```\n{str(e)}\n```\n\n"
                        "Double-check your `MISTRAL_API_KEY` and internet connection, then try again."
                    )

            st.markdown(response)
            ai_idx = len(st.session_state.messages)  # index this AI message will occupy
            ts_now = datetime.now().strftime("%H:%M")
            st.markdown(f"<div class='msg-timestamp' style='text-align:left;'>{ts_now}</div>", unsafe_allow_html=True)

        # 3. Add AI message to state
        st.session_state.messages.append(AIMessage(content=response))
        st.session_state.meta[ai_idx] = {"time": ts_now}
