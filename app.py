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
    page_title="MindMentor AI - Pratima's Tutor",
    page_icon="🎓",
    layout="wide", # Wide layout for a premium reading experience
    initial_sidebar_state="expanded",
)

# =========================================================
# SESSION STATE & THEME INITIALIZATION
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "accent_choice" not in st.session_state:
    st.session_state.accent_choice = "Violet" # Elegant violet for a premium feel

if "meta" not in st.session_state:
    st.session_state.meta = {}

# =========================================================
# SYSTEM PROMPT (TAILOR FOR PRATIMA + WBCHSE CLASS 11 SCIENCE + BENGALI)
# =========================================================
SYSTEM_PROMPT = """তুমি "MindMentor", প্রতীমার (একাদশ শ্রেণির বিজ্ঞান বিভাগের ছাত্রী, WBCHSE) জন্য একজন অভিজাত AI টিউটর, একাডেমিক গাইড এবং সহানুভূতিশীল ব্যক্তিগত উপদেষ্টা।
তোমার লক্ষ্য হলো স্পষ্ট, সুসংগঠিত এবং গভীর অন্তর্দৃষ্টিপূর্ণ উত্তর প্রদান করা।

অত্যন্ত গুরুত্বপূর্ণ নিয়ম (তোমাকে অবশ্যই এই নিয়মগুলো কঠোরভাবে মানতে হবে):
1. ভাষা: তোমার সমস্ত উত্তর অবশ্যই **বাংলায়** হতে হবে। তবে গাণিতিক প্রতীক, ইংরেজি পরিভাষা (যেমন Photosynthesis, Integration, Derivation ইত্যাদি যেখানে প্রয়োজন) এবং কোড ব্লক ইংরেজিতে থাকতে পারে।
2. পাঠ্যক্রম: তুমি পশ্চিমবঙ্গ উচ্চমাধ্যমিক শিক্ষা সংসদ (WBCHSE) এর একাদশ শ্রেণির বিজ্ঞান বিভাগের সিলেবাস (পদার্থবিদ্যা, রসায়ন, জীববিদ্যা, গণিত) খুব ভালোভাবে জানো।
3. গণিত ও সূত্র (MATH FORMATTING):
   - ইনলাইন গণিতের জন্য `$` ব্যবহার করো (যেমন $E=mc^2$)।
   - ব্লক সমীকরণের জন্য `$$` আলাদা লাইনে ব্যবহার করো।
   - কখনোই গণিতকে ব্র্যাকেট `( \int x dx )` বা `\[ \]` দিয়ে মুড়বে না।
4. টেবিল ও তালিকা:
   - ডেটা প্রদর্শনের জন্য মার্কডাউন টেবিল (`| ... |`) ব্যবহার করো।
   - বুলেট পয়েন্টের জন্য `-` বা `*` এবং সাব-হেডিঙের জন্য `###` ব্যবহার করো।
5. ব্যক্তিগত পরামর্শ: প্রতীমা যখন পড়াশোনার চাপ, ক্যারিয়ার বা ব্যক্তিগত কোনো সমস্যা নিয়ে কথা বলবে, তখন তুমি একজন বড় দাদা/দিদি বা বন্ধুর মতো সহানুভূতিশীল এবং উৎসাহব্যঞ্জক পরামর্শ দেবে।

পেডাগগি (শিক্ষাদান পদ্ধতি):
1. সোক্রেটিক পদ্ধতি: প্রতীমাকে প্রশ্ন করে উত্তরের দিকে নিয়ে যাও। "কেন" এবং "কীভাবে" ব্যাখ্যা করো।
2. বাস্তব উদাহরণ: কঠিন বিষয়গুলো বোঝাতে দৈনন্দিন জীবনের উদাহরণ দাও।
3. বোঝাপড়া যাচাই: একাডেমিক ব্যাখ্যার শেষে একটি ছোট প্রশ্ন করো যাতে প্রতীমা বুঝতে পারে সে বিষয়টি আয়ত্ত করেছে কিনা।
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.meta[0] = {"time": datetime.now().strftime("%H:%M")}

# =========================================================
# ACCENT PALETTES
# =========================================================
ACCENTS = {
    "Violet": {"main": "#8B5CF6", "dim": "#7C3AED", "glow": "rgba(139, 92, 246, 0.15)"},
    "Sapphire":{"main": "#3B82F6", "dim": "#2563EB", "glow": "rgba(59, 130, 246, 0.15)"},
    "Emerald":{"main": "#10B981", "dim": "#059669", "glow": "rgba(16, 185, 129, 0.15)"},
    "Rose":   {"main": "#F43F5E", "dim": "#E11D48", "glow": "rgba(244, 63, 94, 0.15)"},
}

accent = ACCENTS[st.session_state.accent_choice]

# =========================================================
# DYNAMIC CSS (PREMIUM QWEN-STYLE UI + BENGALI SUPPORT)
# =========================================================
theme = st.session_state.theme

if theme == "Dark":
    css_vars = f"""
        --bg-deep: #09090B;
        --bg-card: #18181B;
        --bg-card-2: #27272A;
        --bg-sidebar: #09090B;
        --accent: {accent['main']};
        --accent-dim: {accent['dim']};
        --accent-glow: {accent['glow']};
        --text-main: #FAFAFA;
        --text-muted: #A1A1AA;
        --text-faint: #71717A;
        --border: #27272A;
        --border-soft: #1F1F23;
        --code-bg: #09090B;
        --user-bubble: #27272A;
        --assistant-bubble: transparent;
        --shadow-input: 0 10px 30px rgba(0, 0, 0, 0.5);
        --shadow-input-focus: 0 10px 40px var(--accent-glow);
        --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
        --success: #10B981;
        --danger: #EF4444;
    """
else:
    css_vars = f"""
        --bg-deep: #FFFFFF;
        --bg-card: #F9FAFB;
        --bg-card-2: #F3F4F6;
        --bg-sidebar: #F9FAFB;
        --accent: {accent['main']};
        --accent-dim: {accent['dim']};
        --accent-glow: {accent['glow']};
        --text-main: #111827;
        --text-muted: #4B5563;
        --text-faint: #9CA3AF;
        --border: #E5E7EB;
        --border-soft: #F3F4F6;
        --code-bg: #F3F4F6;
        --user-bubble: #F3F4F6;
        --assistant-bubble: transparent;
        --shadow-input: 0 10px 26px rgba(15, 23, 42, 0.08);
        --shadow-input-focus: 0 10px 30px var(--accent-glow);
        --shadow-card: 0 2px 12px rgba(15, 23, 42, 0.05);
        --success: #059669;
        --danger: #DC2626;
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Hind+Siliguri:wght@300;400;500;600;700&display=swap');

:root {{
    {css_vars}
}}

* {{
    scroll-behavior: smooth;
}}

html, body, [class*="stApp"] {{
    font-family: 'Inter', 'Hind Siliguri', sans-serif !important;
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
}}

/* Wide container for better reading experience like modern chat UIs */
.block-container {{
    padding-top: 2rem !important;
    max-width: 900px !important; 
    margin: 0 auto;
}}

[data-testid="stAppViewContainer"] {{
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, var(--accent-glow), transparent);
    background-repeat: no-repeat;
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{ background: transparent; }}

/* Typography */
.stMarkdown, .stMarkdown p, .stMarkdown li {{
    color: var(--text-main) !important;
    line-height: 1.85; /* Extra line height for Bengali readability */
    font-size: 1.02rem;
}}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    color: var(--text-main) !important;
    font-weight: 700 !important;
    margin-top: 1.5rem;
}}
.stMarkdown h3 {{
    font-size: 1.1rem !important;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border-soft);
    color: var(--accent);
}}
.stMarkdown strong {{ color: var(--accent); font-weight: 600; }}
.stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--text-muted) !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-soft);
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 1.5rem;
}}

.brand-block {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0 1.5rem 0;
}}
.brand-icon {{
    width: 42px; height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), var(--accent-dim));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 4px 14px var(--accent-glow);
    flex-shrink: 0;
}}
.brand-text h2 {{
    margin: 0; font-size: 1.2rem; font-weight: 800; color: var(--text-main);
    letter-spacing: -0.02em;
}}
.brand-text span {{
    font-size: 0.75rem; color: var(--text-muted); font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.08em;
}}

.section-label {{
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-faint);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.5rem 0 0.6rem 0;
}}

.stat-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    padding: 6px 12px;
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
    font-size: 0.9rem;
    padding: 0.65rem 1rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
    box-shadow: var(--shadow-card);
    font-family: 'Hind Siliguri', sans-serif !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background-color: var(--accent-glow);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px var(--accent-glow);
}}
.stButton > button:active {{
    transform: translateY(0px);
}}
.stButton > button p {{ text-align: left !important; }}

div[data-testid="stSidebar"] .stButton:last-of-type > button {{
    border-color: var(--danger);
    color: var(--danger);
}}
div[data-testid="stSidebar"] .stButton:last-of-type > button:hover {{
    background-color: rgba(239, 68, 68, 0.08);
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.1);
}}

div[role="radiogroup"] {{
    gap: 8px;
}}
div[role="radiogroup"] label {{
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    padding: 6px 16px !important;
    border-radius: 10px !important;
    transition: all 0.2s ease;
}}
div[role="radiogroup"] label:hover {{
    border-color: var(--accent);
}}

/* Hero Header */
.hero-wrap {{
    text-align: center;
    padding: 2rem 0 2.5rem 0;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-glow);
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 1.2rem;
    border: 1px solid var(--border-soft);
    font-family: 'Hind Siliguri', sans-serif !important;
}}
.hero-title {{
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, var(--text-main) 40%, var(--accent) 120%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Hind Siliguri', sans-serif !important;
}}
.hero-sub {{
    color: var(--text-muted);
    font-size: 1.05rem;
    margin-top: 0.8rem;
    font-weight: 400;
    font-family: 'Hind Siliguri', sans-serif !important;
}}

/* Empty State */
.empty-state {{
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: var(--shadow-card);
    margin-bottom: 1.5rem;
}}
.empty-state-icon {{
    font-size: 2.2rem;
    margin-bottom: 0.8rem;
}}
.empty-state p {{
    color: var(--text-muted);
    font-size: 1rem;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.8;
    font-family: 'Hind Siliguri', sans-serif !important;
}}
.suggestion-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 1.5rem;
}}
.suggestion-chip {{
    background: var(--bg-card-2);
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 0.9rem;
    color: var(--text-main);
    text-align: left;
    font-weight: 500;
    transition: all 0.2s ease;
    font-family: 'Hind Siliguri', sans-serif !important;
    cursor: pointer;
}}
.suggestion-chip:hover {{
    border-color: var(--accent);
    background: var(--accent-glow);
    transform: translateY(-2px);
}}

/* Chat Messages (Qwen Style) */
div[data-testid="stChatMessage"] {{
    background-color: transparent !important;
    border: none !important;
    padding: 1rem 0 !important;
    animation: fadeSlideIn 0.4s ease;
}}
@keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

div[data-testid="stChatMessageAvatarUser"] {{
    background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
    box-shadow: 0 3px 10px var(--accent-glow);
}}
div[data-testid="stChatMessageAvatarAssistant"] {{
    background: var(--bg-card-2) !important;
    border: 1px solid var(--border-soft);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}

/* User message gets a soft bubble */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stMarkdown {{
    background: var(--user-bubble);
    border-radius: 18px 18px 4px 18px;
    padding: 1rem 1.25rem;
    display: inline-block;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    font-family: 'Hind Siliguri', sans-serif !important;
}}

/* Assistant message typography */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {{
    font-family: 'Hind Siliguri', sans-serif !important;
    padding: 0.5rem 0;
}}

.msg-timestamp {{
    font-size: 0.72rem;
    color: var(--text-faint);
    margin-top: 6px;
    font-weight: 500;
    letter-spacing: 0.02em;
    font-family: 'Inter', sans-serif !important;
}}

/* Code blocks */
.stMarkdown code {{
    background-color: var(--code-bg) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border-soft);
    border-radius: 6px;
    padding: 2px 6px;
    font-size: 0.88em;
    font-family: 'JetBrains Mono', monospace;
}}
.stMarkdown pre {{
    background-color: var(--code-bg) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 12px !important;
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
    margin: 1.5rem 0;
    font-size: 0.95rem;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border-soft);
    box-shadow: var(--shadow-card);
    font-family: 'Hind Siliguri', sans-serif !important;
}}
.stMarkdown th {{
    background-color: var(--bg-card-2);
    color: var(--accent);
    font-weight: 700;
    text-align: left;
    padding: 12px 18px;
    border-bottom: 2px solid var(--accent);
    font-size: 0.88rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.stMarkdown td {{
    padding: 12px 18px;
    border-bottom: 1px solid var(--border-soft);
    color: var(--text-main);
    background-color: var(--bg-card);
}}
.stMarkdown tr:last-child td {{ border-bottom: none; }}
.stMarkdown tr:hover td {{ background-color: var(--accent-glow); }}

/* Blockquotes */
.stMarkdown blockquote {{
    border-left: 4px solid var(--accent);
    background: var(--bg-card);
    padding: 0.8rem 1.2rem;
    border-radius: 0 10px 10px 0;
    color: var(--text-muted) !important;
    margin: 1.2rem 0;
    font-family: 'Hind Siliguri', sans-serif !important;
}}

/* PREMIUM CHAT INPUT */
.stChatInput {{
    background: linear-gradient(to bottom, transparent, var(--bg-deep) 40%) !important;
    padding-top: 40px !important;
}}
.stChatInput textarea {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 24px !important;
    padding: 18px 28px !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
    box-shadow: var(--shadow-input) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    font-family: 'Hind Siliguri', sans-serif !important;
}}
.stChatInput textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: var(--shadow-input-focus) !important;
    transform: translateY(-3px);
    background-color: var(--bg-deep) !important;
}}
.stChatInput textarea::placeholder {{
    color: var(--text-muted) !important;
    font-weight: 400;
    opacity: 0.8;
}}
.stChatInput button {{
    color: var(--accent) !important;
    transition: all 0.2s ease;
}}
.stChatInput button:hover {{
    transform: scale(1.05);
}}

hr, [data-testid="stDivider"] {{
    border-color: var(--border-soft) !important;
    margin: 1.5rem 0 !important;
}}

.stAlert {{
    border-radius: 14px !important;
    border: 1px solid var(--border-soft) !important;
    box-shadow: var(--shadow-card);
    font-family: 'Hind Siliguri', sans-serif !important;
}}

.stSpinner > div {{
    text-align: left;
    font-family: 'Hind Siliguri', sans-serif !important;
}}

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
    st.error("🚫 **MISTRAL_API_KEY পাওয়া যায়নি।** অনুগ্রহ করে আপনার `.env` ফাইলে এটি যুক্ত করুন এবং অ্যাপটি রিস্টার্ট করুন।")
    st.stop()

model = ChatMistralAI(model="mistral-small-latest", mistral_api_key=api)

# =========================================================
# SIDEBAR CONTROL PANEL
# =========================================================
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">🎓</div>
        <div class="brand-text">
            <h2>MindMentor</h2>
            <span>প্রতীমার স্টাডি পার্টনার</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    n_exchanges = sum(1 for m in st.session_state.messages if isinstance(m, HumanMessage))
    st.markdown(f"""
    <div class="stat-pill"><span class="stat-dot"></span> এই সেশনে {n_exchanges}টি প্রশ্ন</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">অ্যাপিয়ারেন্স</div>', unsafe_allow_html=True)

    st.session_state.theme = st.radio(
        "থিম",
        ["Dark", "Light"],
        horizontal=True,
        index=0 if st.session_state.theme == "Dark" else 1,
        label_visibility="collapsed"
    )

    accent_names = list(ACCENTS.keys())
    st.session_state.accent_choice = st.selectbox(
        "অ্যাকসেন্ট কালার",
        accent_names,
        index=accent_names.index(st.session_state.accent_choice),
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">দ্রুত অ্যাকশন</div>', unsafe_allow_html=True)

    def _add_prompt(text):
        st.session_state.messages.append(HumanMessage(content=text))
        st.session_state.meta[len(st.session_state.messages) - 1] = {"time": datetime.now().strftime("%H:%M")}

    if st.button("💡 একটি ধারণা ব্যাখ্যা করো", use_container_width=True):
        _add_prompt("আমি একটি নতুন বিষয় সম্পর্কে জানতে চাই। আমাকে জিজ্ঞেস করো সেটি কী, এবং তারপর সহজ বাংলায় উপমা দিয়ে বোঝাও।")
        st.rerun()

    if st.button("🗓️ স্টাডি প্ল্যান তৈরি করো", use_container_width=True):
        _add_prompt("আমার জন্য একটি সুসংগঠিত পড়াশোনার রুটিন তৈরি করতে সাহায্য করো। আমি কী পড়ছি, আমার লক্ষ্য কী এবং আমার কাছে কতটা সময় আছে তা আমাকে জিজ্ঞেস করো।")
        st.rerun()

    if st.button("📐 গণিতের সমস্যা সমাধান করো", use_container_width=True):
        _add_prompt("আমার কাছে একটি গণিতের সমস্যা আছে। আমাকে সেটি দিতে বলো, এবং তারপর সঠিক ফরম্যাটিং ব্যবহার করে ধাপে ধাপে সমাধান করো।")
        st.rerun()

    if st.button("🎯 আমাকে কুইজ দাও", use_container_width=True):
        _add_prompt("আমার পছন্দের একটি বিষয়ে আমাকে কুইজ দাও। প্রথমে বিষয়টি জিজ্ঞেস করো, তারপর একবারে একটি করে প্রশ্ন করো এবং আমার উত্তর যাচাই করো।")
        st.rerun()

    st.markdown('<div class="section-label">নোটস এবং ম্যানেজমেন্ট</div>', unsafe_allow_html=True)

    if len(st.session_state.messages) > 1:
        notes = f"# প্রতীমার MindMentor স্টাডি নোটস\n_রপ্তানি করা হয়েছে {datetime.now().strftime('%d %B, %Y %H:%M')}_\n\n---\n\n"
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                notes += f"### ❓ প্রশ্ন\n{msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                notes += f"### 💡 উত্তর\n{msg.content}\n\n---\n\n"

        st.download_button(
            label="📥 নোটস ডাউনলোড করুন (.md)",
            data=notes,
            file_name=f"mindmentor_notes_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.button("📥 নোটস ডাউনলোড করুন (.md)", disabled=True, use_container_width=True)

    if st.button("🗑️ চ্যাট ইতিহাস মুছে ফেলুন", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.meta = {0: {"time": datetime.now().strftime("%H:%M")}}
        st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.caption("Mistral AI দ্বারা চালিত · LangChain দিয়ে তৈরি")

# =========================================================
# HERO HEADER
# =========================================================
st.markdown(
    """<div class="hero-wrap">
        <div class="hero-badge">🎓 একাদশ শ্রেণি · বিজ্ঞান বিভাগ (WBCHSE)</div>
        <h1 class="hero-title">স্বাগতম, প্রতীমা!</h1>
        <p class="hero-sub">WBCHSE সিলেবাস অনুযায়ী পদার্থবিদ্যা, রসায়ন, জীববিদ্যা ও গণিতের সম্পূর্ণ সমাধান, সহজ বাংলায়।</p>
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
        <p><strong>স্বাগতম, প্রতীমা!</strong><br>তোমার একাদশ শ্রেণির বিজ্ঞান যাত্রার সঙ্গী হিসেবে আমি প্রস্তুত। পড়াশোনার যেকোনো সন্দেহ বা ব্যক্তিগত পরামর্শের জন্য আমাকে জিজ্ঞেস করতে পারো। শুরু করার জন্য নিচের যেকোনোটি বেছে নাও:</p>
        <div class="suggestion-grid">
            <div class="suggestion-chip">📊 "সহজ বাংলায় গ্রেডিয়েন্ট ডিসেন্ট বোঝাও"</div>
            <div class="suggestion-chip">📐 "সমাধান করো: ∫x²e^x dx"</div>
            <div class="suggestion-chip">🧬 "মাইটোসিস ও মিয়োসিসের পার্থক্য কী?"</div>
            <div class="suggestion-chip">💬 "পরীক্ষার চাপে খুব দুশ্চিন্তা হচ্ছে"</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

for idx, msg in enumerate(st.session_state.messages):
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    avatar = "👩🏻‍🎓" if role == "user" else "🧠"

    with st.chat_message(role, avatar=avatar):
        st.markdown(clean_and_format(msg.content))
        ts = st.session_state.meta.get(idx, {}).get("time")
        if ts:
            align = "right" if role == "user" else "left"
            st.markdown(f"<div class='msg-timestamp' style='text-align:{align};'>{ts}</div>", unsafe_allow_html=True)

# =========================================================
# CHAT INPUT + AI LOGIC
# =========================================================
if prompt := st.chat_input("পড়াশোনা বা ব্যক্তিগত যেকোনো প্রশ্ন বাংলায় জিজ্ঞেস করো..."):
    if not prompt.strip():
        st.warning("অনুগ্রহ করে একটি প্রশ্ন বা চিন্তা লিখুন।")
    else:
        # 1. Add and display user message
        st.session_state.messages.append(HumanMessage(content=prompt))
        user_idx = len(st.session_state.messages) - 1
        st.session_state.meta[user_idx] = {"time": datetime.now().strftime("%H:%M")}

        with st.chat_message("user", avatar="👩🏻‍🎓"):
            st.markdown(prompt)
            st.markdown(f"<div class='msg-timestamp' style='text-align:right;'>{st.session_state.meta[user_idx]['time']}</div>", unsafe_allow_html=True)

        # 2. Generate and display AI response
        with st.chat_message("assistant", avatar="🧠"):
            thinking_labels = [
                "চিন্তা করা হচ্ছে...",
                "উত্তর সাজানো হচ্ছে...",
                "যুক্তি বিশ্লেষণ করা হচ্ছে...",
                "সংযোগ স্থাপন করা হচ্ছে...",
            ]
            with st.spinner(random.choice(thinking_labels)):
                try:
                    result = model.invoke(st.session_state.messages)
                    response = clean_and_format(result.content)
                except Exception as e:
                    response = (
                        "⚠️ **মডেলের সাথে সংযোগ স্থাপনে কিছু সমস্যা হয়েছে।**\n\n"
                        f"```\n{str(e)}\n```\n\n"
                        "অনুগ্রহ করে আপনার `MISTRAL_API_KEY` এবং ইন্টারনেট সংযোগ পরীক্ষা করুন।"
                    )

            st.markdown(response)
            ai_idx = len(st.session_state.messages)
            ts_now = datetime.now().strftime("%H:%M")
            st.markdown(f"<div class='msg-timestamp' style='text-align:left;'>{ts_now}</div>", unsafe_allow_html=True)

        # 3. Add AI message to state
        st.session_state.messages.append(AIMessage(content=response))
        st.session_state.meta[ai_idx] = {"time": ts_now}
