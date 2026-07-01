import os
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
}

/* ---- chat bubbles ---- */
.bubble-row {
    display: flex;
    gap: 10px;
    margin: 14px 0;
    align-items: flex-start;
}
.bubble-row.user { flex-direction: row-reverse; }

.avatar {
    font-size: 1.3rem;
    background: var(--mic-charcoal);
    border-radius: 50%;
    width: 38px;
    height: 38px;
    min-width: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(242, 183, 5, 0.35);
}

.bubble {
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 75%;
    line-height: 1.5;
    font-size: 0.96rem;
}

.bubble.ai {
    background: var(--mic-charcoal);
    border: 1px solid rgba(242, 183, 5, 0.35);
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
    padding: 22px;
    margin-top: 10px;
}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] {
    background: var(--mic-charcoal);
    border-right: 1px solid rgba(242, 183, 5, 0.2);
}

/* ---- buttons ---- */
.stButton > button {
    background: transparent;
    border: 1.5px solid var(--spotlight-gold);
    color: var(--spotlight-gold);
    border-radius: 10px;
    font-family: 'Space Mono', monospace;
    transition: background 0.15s ease, color 0.15s ease;
}
.stButton > button:hover {
    background: var(--spotlight-gold);
    color: var(--stage-black);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="stage-eyebrow">🎤 Now on stage</div>', unsafe_allow_html=True)
st.markdown('<div class="stage-title">Open Mic AI</div>', unsafe_allow_html=True)
st.markdown('<div class="stage-sub">A chatbot with questionable comedic timing, powered by Mistral.</div>', unsafe_allow_html=True)
st.markdown('<div class="marquee-lights"></div>', unsafe_allow_html=True)

# =========================================================
# AI SETUP (unchanged)
# =========================================================
load_dotenv()
api = os.getenv("MISTRAL_API_KEY")

if not api:
    st.error("🚫 **MISTRAL_API_KEY not found.** Add it to your `.env` file and restart the app.")
    st.stop()

model = ChatMistralAI(model="mistral-small-2506", mistral_api_key=api)

# =========================================================
# SESSION STATE (unchanged messages list + AI persona)
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content="You are a funny assistant.")]

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
    st.metric("Jokes told", jokes_told)

    with st.expander("🎬 Director's notes (system prompt)"):
        st.write(st.session_state.messages[0].content)

    st.divider()

    if st.button("🧹 Clear the stage", use_container_width=True):
        st.session_state.messages = [SystemMessage(content="You are a funny assistant.")]
        st.session_state.chat_ended = False
        st.rerun()

    st.caption("Type `0` in the chat to leave the show.")

# =========================================================
# CHAT FEED (display only — reads the same message list the AI uses)
# =========================================================
has_conversation = any(not isinstance(m, SystemMessage) for m in st.session_state.messages)

if not has_conversation and not st.session_state.chat_ended:
    st.markdown(
        '<div class="empty-state">🎬 The mic is live — say something to get the show started.</div>',
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "ai"
    avatar = "🗣️" if role == "user" else "🎤"
    st.markdown(
        f"""<div class="bubble-row {role}">
                <div class="avatar">{avatar}</div>
                <div class="bubble {role}">{msg.content}</div>
            </div>""",
        unsafe_allow_html=True,
    )

# =========================================================
# END-OF-SHOW STATE
# =========================================================
if st.session_state.chat_ended:
    st.info("🎬 That's a wrap! Thanks for stopping by the open mic.")
    if st.button("🎤 Restart the show"):
        st.session_state.messages = [SystemMessage(content="You are a funny assistant.")]
        st.session_state.chat_ended = False
        st.rerun()

else:
    # =====================================================
    # CHAT INPUT + AI LOGIC (unchanged: same append → validate → invoke → append)
    # =====================================================
    user_input = st.chat_input("Heckle away 🎤 (type 0 to leave the show)")

    if user_input:
        if user_input == "0":
            st.session_state.chat_ended = True
        else:
            # Append user message
            st.session_state.messages.append(HumanMessage(content=user_input))

            # Validate input
            if not user_input.strip():
                st.error("Prompt cannot be empty")
            else:
                # Get AI response
                with st.spinner("🎙️ Workshopping a comeback..."):
                    result = model.invoke(st.session_state.messages)
                st.session_state.messages.append(AIMessage(content=result.content))

        st.rerun()
give me the recquirment.txt file for that
