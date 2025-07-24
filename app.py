import streamlit as st
import openai
import os
import base64
from io import BytesIO
from datetime import datetime
import requests

# ---------- 🌟 PAGE CONFIG ----------
st.set_page_config(page_title="Mandala Generator", layout="wide")

# ---------- 🎨 CUSTOM CSS ----------
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
        font-family: 'Montserrat', sans-serif;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        color: white;
        background-color: #2e2e2e;
    }
    .caption-box {
        font-style: italic;
        color: #ccc;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .download-btn {
        position: absolute;
        top: 10px;
        right: 10px;
    }
    .chat-history-scroll {
        overflow-y: auto;
        max-height: 90vh;
        padding: 10px;
        background-color: #2a2a2a;
        border-radius: 10px;
    }
    .close-btn {
        text-align: right;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- 🧳 SESSION STATE ----------
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'show_history' not in st.session_state:
    st.session_state['show_history'] = True
if 'openai_key' not in st.session_state:
    st.session_state['openai_key'] = ''

# ---------- 🧠 FUNCTIONS ----------
def generate_caption(age, mood):
    tone = "muted tones and slow floral layers" if "sad" in mood.lower() or "tired" in mood.lower() else \
           "vibrant colors and blooming symmetry" if "joy" in mood.lower() else \
           "light patterns and playful symmetry" if int(age) < 20 else \
           "earthy hues and balanced geometry"
    return f"Age {age}, feeling {mood.lower()} → {tone}"

def generate_mandala(age, mood):
    openai.api_key = st.session_state['openai_key']
    prompt = f"Generate a calming, symmetrical mandala art inspired by the emotional state '{mood}' for someone aged {age}. Focus on symmetry, texture, colors, and emotional healing."
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

def image_to_base64_url(url):
    image_data = requests.get(url).content
    encoded = base64.b64encode(image_data).decode()
    return f"data:image/png;base64,{encoded}"

def download_chat_history():
    lines = [
        f"{e['timestamp']} - Age {e['age']} - Mood: {e['mood']}\n{e['caption']}\n{e['image_url']}\n"
        for e in st.session_state.history
    ]
    content = "\n---\n".join(lines)
    b = BytesIO()
    b.write(content.encode())
    b.seek(0)
    return b

# ---------- 🖼️ LAYOUT ----------
left, main = st.columns([1, 3])

# ---------- 📁 LEFT PANE: CHAT HISTORY ----------
with left:
    if st.session_state['show_history']:
        with st.container():
            st.markdown("<div class='chat-history-scroll'>", unsafe_allow_html=True)
            if st.button("Close Chat History", key="close_history"):
                st.session_state['show_history'] = False
                st.rerun()
            if not st.session_state.history:
                st.info("No mandalas generated yet.")
            else:
                for i, entry in enumerate(st.session_state.history):
                    with st.expander(f"{entry['timestamp']} | Age {entry['age']} | Mood: {entry['mood'].capitalize()}", expanded=False):
                        st.image(entry["image_url"], caption=entry["caption"], use_column_width=True)
                        b64_img = image_to_base64_url(entry["image_url"])
                        st.markdown(f'<a href="{b64_img}" download="mandala_{i+1}.png">Download Image</a>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.button("Open Chat History", key="open_history"):
            st.session_state['show_history'] = True
            st.rerun()

# ---------- 🧘 MAIN INPUT & OUTPUT ----------
with main:
    st.markdown("<h1 style='text-align:center;'>Mandala Generator</h1>", unsafe_allow_html=True)

    with st.form("user_input", clear_on_submit=False):
        st.markdown("### Enter your OpenAI API Key")
        st.session_state['openai_key'] = st.text_input("API Key", type="password")

        st.markdown("### Share your mood & age")
        age = st.number_input("Age", min_value=5, max_value=100, value=25)
        mood = st.text_input("Current Mood", placeholder="e.g. calm, sad, joyful")
        submitted = st.form_submit_button("Generate Mandala")

    if submitted and mood.strip() and st.session_state['openai_key']:
        with st.spinner("Generating your personalized mandala..."):
            try:
                image_url = generate_mandala(age, mood)
                caption = generate_caption(age, mood)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.history.insert(0, {
                    "image_url": image_url,
                    "caption": caption,
                    "timestamp": timestamp,
                    "age": age,
                    "mood": mood
                })
                st.image(image_url, caption=caption, use_column_width=True)
                b64_img = image_to_base64_url(image_url)
                st.markdown(f'<a href="{b64_img}" download="mandala.png">Download Mandala</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error("Failed to generate mandala. Please check your API key and try again.")

    if st.session_state.history:
        st.markdown("---")
        st.download_button("Download Chat History", data=download_chat_history(), file_name="mandala_chat_history.txt", mime="text/plain")
