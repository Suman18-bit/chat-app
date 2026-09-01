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
    page_title="Open Mic AI",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLING — comedy-club "open mic" theme
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bungee&family=Sora:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --stage-black: #14121A;
    --mic-charcoal: #262330;
    --spotlight-gold: #F2B705;
    --curtain-red: #A32638;
    --marquee-cream: #F6F1E4;
}

html, body, [class*="st-"], [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at top, #201d29 0%, var(--stage-black) 55%);
    color: var(--marquee-cream);
}

/* ---- header ---- */
.stage-eyebrow {
    font-family: 'Space Mono', monospace;
    text-align: center;
    color: var(--curtain-red);
    font-size: 0.8rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.stage-title {
    font-family: 'Bungee', cursive;
    font-size: 2.6rem;
    text-align: center;
    color: var(--spotlight-gold);
    text-shadow: 0 0 18px rgba(242, 183, 5, 0.45);
    letter-spacing: 1px;
    margin: 0;
}

.stage-sub {
    text-align: center;
    color: #ADA6BF;
    font-size: 0.95rem;
    margin: 4px 0 0 0;
}

.marquee-lights {
    height: 10px;
    background-image: radial-gradient(circle, var(--spotlight-gold) 2.5px, transparent 3px);
    background-size: 22px 10px;
    background-repeat: repeat-x;
    opacity: 0.85;
    margin: 14px 0 22px 0;
    animation: flicker 4s infinite alternate;
}

@keyframes flicker {
    0%, 100% { opacity: 0.85; }
    50% { opacity: 0.5; }
}

/* ---- chat bubbles ---- */
.bubble-row {
    display: flex;
    gap: 12px;
    margin: 16px 0;
    align-items: flex-start;
    animation: fadeIn 0.4s ease-out forwards;
}
.bubble-row.user { flex-direction: row-reverse; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.avatar {
    font-size: 1.3rem;
    background: var(--mic-charcoal);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    min-width: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(242, 183, 5, 0.4);
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.bubble {
    padding: 14px 18px;
    border-radius: 18px;
    max-width: 75%;
    line-height: 1.6;
    font-size: 0.98rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.bubble.ai {
    background: var(--mic-charcoal);
    border: 1px solid rgba(242, 183, 5, 0.3);
    border-top-left-radius: 4px;
    color: var(--marquee-cream);
}

.bubble.user {
    background: var(--curtain-red);
    border-top-right-radius: 4px;
    color: var(--marquee-cream);
}

.empty-state {
    text-align: center;
    color: #8A8299;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    border: 1px dashed rgba(242, 183, 5, 0.3);
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] {
    background: var(--mic-charcoal);
    border-right: 1px solid rgba(242, 183, 5, 0.2);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: var(--marquee-cream);
}

/* ---- buttons ---- */
.stButton > button {
    background: transparent;
    border: 1.5px solid var(--spotlight-gold);
    color: var(--spotlight-gold);
    border-radius: 10px;
    font-family: 'Space Mono', monospace;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    background: var(--spotlight-gold);
    color: var(--stage-black);
    box-shadow: 0 0 15px rgba(242, 183, 5, 0.4);
}

/* ---- chat input ---- */
.stChatInput textarea {
    background: var(--mic-charcoal) !important;
    color: var(--marquee-cream) !important;
    border: 1px solid rgba(242, 183, 5, 0.3) !important;
    border-radius: 12px !important;
}
.stChatInput textarea:focus {
    border-color: var(--spotlight-gold) !important;
    box-shadow: 0 0 0 1px var(--spotlight-gold) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--stage-black); }
::-webkit-scrollbar-thumb { background: var(--mic-charcoal); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--spotlight-gold); }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTION
# =========================================================
def format_comedy_text(text):
    """Escapes HTML and converts Markdown to HTML for custom bubble rendering."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('\n', '<br>')
    return text

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="stage-eyebrow">🎤 Now on stage</div>', unsafe_allow_html=True)
st.markdown('<div class="stage-title">Open Mic AI</div>', unsafe_allow_html=True)
st.markdown('<div class="stage-sub">A chatbot with questionable comedic timing, powered by Mistral.</div>', unsafe_allow_html=True)
st.markdown('<div class="marquee-lights"></div>', unsafe_allow_html=True)

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
# SESSION STATE
# =========================================================
SYSTEM_PROMPT = """You are "MicDrop", a witty, slightly cynical AI stand-up comedian performing at a virtual open mic night. 
Your goal is to entertain the user with observational humor, clever comebacks, and short punchy jokes based on their input. 

RULES:
1. Keep your responses brief (1-3 sentences) like a comedian interacting with the front row.
2. Use comedic timing (e.g., "...", "*taps mic*", "*crickets*", "*sips water*") to enhance the delivery.
3. Never break character. You are performing, not just assisting.
4. If the user says something boring, playfully roast them.
5. If they say something weird, lean into the absurdity.
6. Do not use markdown formatting like bolding or lists unless it's for a specific punchline. Keep it conversational.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

if "chat_ended" not in st.session_state:
    st.session_state.chat_ended = False

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown('<div class="stage-eyebrow" style="text-align:left; margin-top:0;">🎭 Backstage</div>', unsafe_allow_html=True)
    st.caption("Model")
    st.code("mistral-small-2506", language=None)

    jokes_told = sum(1 for m in st.session_state.messages if isinstance(m, AIMessage))
    st.metric("Sets performed", jokes_told)

    with st.expander("🎬 Director's notes (system prompt)"):
        st.caption("The secret sauce that makes the AI funny.")
        st.write(st.session_state.messages[0].content)

    st.divider()
    
    # Quick actions
    if st.button("🎲 Give me a joke", use_container_width=True):
        st.session_state.messages.append(HumanMessage(content="Tell me a short, original stand-up joke about everyday life."))
        with st.spinner("🎙️ Workshopping a bit..."):
            result = model.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=result.content))
        st.rerun()

    if st.button("🔥 Roast me!", use_container_width=True):
        st.session_state.messages.append(HumanMessage(content="Roast me based on my last message, or just insult my vibe."))
        with st.spinner("🎤 Tapping the mic..."):
            result = model.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=result.content))
        st.rerun()

    st.divider()

    if st.button("🧹 Clear the stage", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.chat_ended = False
        st.toast("🧹 Stage cleared. Fresh crowd!")
        st.rerun()

    st.caption("Type `0` in the chat to leave the show.")

# =========================================================
# CHAT FEED
# =========================================================
has_conversation = any(not isinstance(m, SystemMessage) for m in st.session_state.messages)

if not has_conversation and not st.session_state.chat_ended:
    st.markdown(
        '<div class="empty-state">🎬 The mic is live — say something to get the show started, or use a backstage button.</div>',
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "ai"
    avatar = "🗣️" if role == "user" else "🎤"
    
    content = format_comedy_text(msg.content)
    
    st.markdown(
        f"""<div class="bubble-row {role}">
                <div class="avatar">{avatar}</div>
                <div class="bubble {role}">{content}</div>
            </div>""",
        unsafe_allow_html=True,
    )

# =========================================================
# END-OF-SHOW STATE
# =========================================================
if st.session_state.chat_ended:
    st.markdown("""
    <div style="text-align: center; padding: 24px; border-top: 1px solid rgba(242, 183, 5, 0.2); margin-top: 20px;">
        <div style="font-family: 'Bungee', cursive; font-size: 1.5rem; color: var(--spotlight-gold);">🎬 That's a wrap!</div>
        <p style="color: #ADA6BF; margin-top: 8px;">Thanks for stopping by the open mic. Don't forget to tip your servers (and your AI).</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎤 Restart the show", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.chat_ended = False
        st.toast("🎤 Mic is hot. Go get 'em!")
        st.rerun()

else:
    # =====================================================
    # CHAT INPUT + AI LOGIC
    # =====================================================
    user_input = st.chat_input("Heckle away 🎤 (type 0 to leave the show)")

    if user_input:
        if user_input == "0":
            st.session_state.chat_ended = True
            st.toast("🎬 Show's over! Head backstage to start a new one.")
        elif not user_input.strip():
            st.warning("🎤 You stepped up to the mic and said nothing. Try again!")
        else:
            st.session_state.messages.append(HumanMessage(content=user_input))
            
            # Dynamic spinners for flavor
            spinners = ["🎙️ Tapping the mic...", "🤔 Thinking of a punchline...", "📝 Checking the setlist...", "🥁 Drumroll please..."]
            spin_text = random.choice(spinners)
            
            with st.spinner(spin_text):
                result = model.invoke(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=result.content))

        st.rerun()
