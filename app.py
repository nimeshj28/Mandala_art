import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import random

# ------------------ Config ------------------
st.set_page_config(page_title="Mandala by Mood", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #23074d 0%, #cc5333 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.stTextInput input, .stTextArea textarea {
    background-color: #3c3f58;
    color: white;
    border-radius: 8px;
    font-size: 16px;
}
.stButton>button {
    background-color: #f72585;
    color: white;
    font-weight: bold;
    font-size: 18px;
    border-radius: 12px;
    padding: 0.6em 1.2em;
}
[data-testid="collapsedControl"] {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------ Setup ------------------
if 'history' not in st.session_state:
    st.session_state.history = []

# ------------------ Sidebar ------------------
with st.sidebar:
    st.header("🎒 Your Mandala Journey")
    if st.session_state.history:
        for i, (prompt, img_url, desc) in enumerate(reversed(st.session_state.history)):
            with st.expander(f"🌀 Mandala #{len(st.session_state.history) - i}: {prompt[:25]}"):
                st.image(img_url, caption=desc, use_container_width=True)
                # Download Button
                response = requests.get(img_url)
                img_bytes = BytesIO(response.content)
                b64 = base64.b64encode(img_bytes.getvalue()).decode()
                dl_link = f'<a href="data:image/png;base64,{b64}" download="mandala.png">💾 Download</a>'
                st.markdown(dl_link, unsafe_allow_html=True)
    else:
        st.info("Your sacred spirals will appear here ✨")

# ------------------ Main Area ------------------
st.image("https://i.imgur.com/YZlVgFy.png", width=100)
st.title("🌀 Mandala by Mood")
st.markdown("#### 💭 What's cookin' in your soul today? Let's spin it into sacred geometry!")

# Input Fields
openai_api_key = st.text_input("🔐 Your OpenAI API Key", type="password", placeholder="sk-...")
col1, col2 = st.columns(2)
with col1:
    age = st.text_input("🎂 Drop your age vibe", "27", placeholder="e.g. 27")
with col2:
    emotion = st.text_input("🌈 What's the feeling?", "happy", placeholder="e.g. blissful, anxious, calm")

# Fun interpretations
def interpret_emotion_age(emotion, age):
    templates = [
        f"At {age}, feeling {emotion} means life’s a symphony – love, career, and chaos in perfect rhythm. This mandala echoes harmony from every direction.",
        f"{emotion.title()} at {age}? You’re probably crushing it or at least pretending well 😎 This pattern reflects the cosmic order you're channeling.",
        f"Mandala brewed for a {age}-year-old in a {emotion} mood. Spirals of purpose, petals of passion, and symmetry of the soul.",
        f"Being {age} and feeling {emotion}... that’s some legendary inner alignment. This piece channels that cosmic clarity.",
    ]
    return random.choice(templates)

# Prompt Creator
def make_prompt(emotion, age):
    return f"Black and white symmetrical hand-drawn mandala inspired by a {age}-year-old feeling {emotion}. Intricate, elegant, spiritual, peaceful."

# API Call
def generate_image(api_key, prompt):
    url = "https://api.openai.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1024"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["data"][0]["url"]
    else:
        return None

# Main Button
if st.button("✨ Let’s Brew"):
    if not openai_api_key:
        st.warning("🚫 Don't forget your magic API key!")
    else:
        prompt = make_prompt(emotion, age)
        st.spinner("Spinning sacred threads into patterns... 🧵")
        img_url = generate_image(openai_api_key, prompt)
        if img_url:
            desc = interpret_emotion_age(emotion, age)
            st.image(img_url, caption=desc, use_container_width=True)

            # Add to history
            st.session_state.history.append((prompt, img_url, desc))

            # Download link
            response = requests.get(img_url)
            img_bytes = BytesIO(response.content)
            b64 = base64.b64encode(img_bytes.getvalue()).decode()
            st.markdown(f'<a href="data:image/png;base64,{b64}" download="mandala.png">💾 Download This Mandala</a>', unsafe_allow_html=True)
        else:
            st.error("💥 Couldn’t brew the mandala! Double-check your API key or usage limits.")
