import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# --- Page config ---
st.set_page_config(page_title="Mandala by Mood", layout="wide", initial_sidebar_state="expanded")

# --- Styling ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1f1147 0%, #2e145a 100%);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput input {
        background-color: #393d52;
        color: white;
        border-radius: 6px;
        padding: 0.5rem;
        font-size: 16px;
    }
    .stTextArea textarea {
        background-color: #393d52;
        color: white;
    }
    .stButton>button {
        background-color: #ffffff15;
        color: white;
        border: 1px solid #ffffff30;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-size: 16px;
    }
    .sidebar .sidebar-content {
        background-color: #191933;
    }
    .css-1v3fvcr {
        background-color: #1e1e2f;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title and Sketch ---
st.image("https://i.imgur.com/YZlVgFy.png", width=130)
st.title("🌀 Mandala by Mood")
st.markdown("### 🎨 Hey you, inner art ninja! What’s your vibe today? Let’s paint it in circles of zen.")

# --- Session State for History ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Sidebar History ---
with st.sidebar:
    st.header("🧾 Mandala History")
    if st.session_state.history:
        for i, (prompt, url) in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**Mandala #{len(st.session_state.history) - i}**")
            st.image(url, caption=prompt, use_container_width=True)
            st.markdown("---")
    else:
        st.info("No sacred circles yet 🌕")

# --- Input Fields ---
st.subheader("🔮 Enter your Mandala Mood")

openai_api_key = st.text_input("🔐 Drop Your OpenAI API Key", type="password", placeholder="sk-...")

col1, col2 = st.columns(2)
with col1:
    age = st.text_input("🎂 Your Age Vibe", "25", placeholder="e.g. 25")
with col2:
    emotion = st.text_input("💫 Your Current Emotion", "peaceful", placeholder="e.g. calm, joyful, lost")

# --- Prompt Creator ---
def make_prompt(emotion, age):
    return f"Detailed black and white symmetrical mandala art, inspired by the emotion '{emotion}' and the perspective of a {age}-year-old. Highly artistic, spiritual pattern, clean lines, peaceful aesthetic."

# --- DALL·E Generator ---
def generate_image(api_key, prompt):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    else:
        return None

# --- Download Helper ---
def get_image_download_link(img_url):
    response = requests.get(img_url)
    img_bytes = BytesIO(response.content)
    b64 = base64.b64encode(img_bytes.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="mandala.png">💾 Download Mandala</a>'
    return href

# --- Main Generator ---
if st.button("🎨 Summon Mandala Now"):
    if not openai_api_key:
        st.warning("⚠️ You forgot your secret API scroll!")
    else:
        prompt = make_prompt(emotion, age)
        with st.spinner("✨ Brewing sacred geometry..."):
            img_url = generate_image(openai_api_key, prompt)
            if img_url:
                st.image(img_url, caption=f"Mandala for {age}-year-old feeling '{emotion}'", use_container_width=True)
                st.session_state.history.append((prompt, img_url))

                # Download Button
                st.markdown(get_image_download_link(img_url), unsafe_allow_html=True)
            else:
                st.error("❌ Oops! Couldn't draw your vibe. Check API key or usage limits.")
