import os
import time
from datetime import datetime
import streamlit as st

from src.rag.curator_engine import ArtCuratorEngine
from src.feedback.feedback_hf import log_to_hf_dataset

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Art Curator",
    page_icon="🎨",
    layout="centered"
)

# Define active RAG version tag for evaluation tracking
RAG_VERSION = "custom_v1"

# --- CACHED RAG ENGINE ---
@st.cache_resource
def load_engine():
    """Load and cache the RAG engine instance across Streamlit reruns."""
    return ArtCuratorEngine(keep_alive="5m")

engine = load_engine()

# --- CHAT HISTORY INITIALIZATION ---
if "messages" not in st.session_state:
    welcome_text = (
        "Welcome to your private gallery space. 🎨 "
        "Share your mood, thoughts, or the atmosphere you wish to experience, "
        "and I will curate an artwork for you."
    )
    st.session_state.messages = [
        {
            "role": "assistant",
            "type": "text",
            "content": welcome_text,
        }
    ]

# --- CUSTOM STYLES ---
st.markdown("""
    <style>
    /* Reduce top padding to position header higher */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Chat input border & focus ring */
    div[data-testid="stChatInput"] > div {
        border: 1px solid #3e4451 !important;
    }
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #c5a059 !important; 
        box-shadow: 0 0 6px rgba(197, 160, 89, 0.3) !important;
    }

    /* Chat input submit button (Inactive state) */
    button[data-testid="stChatInputSubmitButton"] {
        background-color: #3e4451 !important; 
        color: #8c92a0 !important; 
        border: none !important;
    }

    /* Chat input submit button (Active state) */
    button[data-testid="stChatInputSubmitButton"]:not(:disabled) {
        background-color: #c5a059 !important; 
        color: white !important; 
    }
    button[data-testid="stChatInputSubmitButton"]:not(:disabled):hover {
        background-color: #b5924f !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- COMPACT UI HEADER ---
st.subheader("🎨 AI Art Curator")
st.caption("Discover artwork tailored to your mood, ideas, and curiosities.")
st.divider()

# --- DISPLAY CHAT HISTORY ---
for idx, msg in enumerate(st.session_state.messages):
    avatar = "🧐" if msg["role"] == "assistant" else "👤"

    with st.chat_message(msg["role"], avatar=avatar):
        if msg["type"] == "text":
            st.write(msg["content"])
            
        elif msg["type"] == "recommendation":
            response = msg["response"]

            if response.guardrail_message:
                st.info(response.guardrail_message)

            if response.clarification_question:
                st.write(response.clarification_question)

            for item in response.recommendations[:1]:
                with st.container(border=True):
                    st.subheader(f"🖼️ {item.title}")

                    if getattr(item, "image_url", None):
                        st.image(item.image_url, use_container_width=True)

                    if item.why_this_artwork:
                        st.markdown(f"💡 Why this artwork:\n{item.why_this_artwork}")

                    if item.curators_note:
                        st.markdown(f"📜 Curator's Note:\n{item.curators_note}")

                    if item.what_to_notice:
                        st.markdown(f"🔍 What to Notice:\n{item.what_to_notice}")

# --- USER INPUT HANDLER ---
if prompt := st.chat_input("Describe your mood, emotions, or the atmosphere you want to feel..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="🧐"):
        with st.spinner("Curating art for you..."):
            start_time = time.time()
            response = engine.generate_response(prompt)
            latency = round(time.time() - start_time, 2)
            
        # 1. Handle guardrails or clarification triggers (bypass feedback block)
        if response.status in ["clarify", "off_topic"]:
            msg_text = response.clarification_question or response.guardrail_message or "Could you please rephrase your request?"
            st.write(msg_text)

            st.session_state.messages.append({
                "role": "assistant",
                "type": "text",
                "content": msg_text
            })

        # 2. Render valid art recommendation card and record feedback metadata
        else:
            if response.guardrail_message:
                st.info(response.guardrail_message)

            for item in response.recommendations[:1]:
                with st.container(border=True):
                    st.subheader(f"🖼️ {item.title}")

                    if getattr(item, "image_url", None):
                        st.image(item.image_url, use_container_width=True)
            
                    if item.why_this_artwork:
                        st.markdown(f"💡 Why this artwork:\n{item.why_this_artwork}")
            
                    if item.curators_note:
                        st.markdown(f"📜 Curator's Note:\n{item.curators_note}")
            
                    if item.what_to_notice:
                        st.markdown(f"🔍 What to Notice:\n{item.what_to_notice}")

            st.session_state.messages.append({
                "role": "assistant",
                "type": "recommendation",
                "response": response,
                "associated_query": prompt
            })

            # Save evaluation metrics strictly for genuine art recommendations
            st.session_state["latest_interaction"] = {
                "user_query": prompt,
                "response_status": response.status,
                "retrieved_art_ids": [
                    rec.artwork_id
                    for rec in (response.recommendations or [])
                    if hasattr(rec, "artwork_id")
                ],
                "latency": latency,
            }

        st.rerun()

# --- FEEDBACK UI (ANCHORED AT BOTTOM) ---
if "latest_interaction" in st.session_state:
    st.write("---")
    st.write("Help evaluate this recommendation:")
    
    rating_val = st.feedback("stars")
    user_comment = st.text_input("Comments (optional):", key="feedback_comment")

    if st.button("Submit Rating"):
        if rating_val is not None:
            interaction = st.session_state["latest_interaction"]

            log_to_hf_dataset(
                rag_version=RAG_VERSION,
                user_query=interaction["user_query"],
                retrieved_art_ids=interaction["retrieved_art_ids"],
                response_status=interaction["response_status"],
                rating=rating_val + 1,  # Convert Streamlit 0-4 index to 1-5 scale
                comment=user_comment,
                response_time_sec=interaction["latency"],
            )

            st.success("Thank you! Feedback recorded for RAG evaluation.")
            # Clear stored interaction state to prevent duplicate submissions
            del st.session_state["latest_interaction"]
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Please select a star rating first.")