import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

st.set_page_config(page_title="Mandala by Mood", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    body {
        background-color: #0f0f0f;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #ffffff10;
        color: white;
        border: 1px solid #ffffff20;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-size: 16px;
    }
    input, textarea {
        background-color: #1e1e1e !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌌 Mandala by Mood")
st.markdown("#### 🎭 Create personalized black & white mandala art based on your **emotion** and **age**.")

# --- Store history in session ---
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- API key input ---
openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password", help="You need your own API key from platform.openai.com")

# --- Friendly inputs ---
col1, col2 = st.columns(2)
with col1:
    age = st.text_input("🧒 Your Age", "25")
with col2:
    emotion = st.text_input("🎨 Your Current Emotion", "peaceful")

# --- Prompt formatting ---
def create_prompt(emotion, age):
    return f"Detailed black and white symmetrical mandala art, inspired by the emotion '{emotion}' and the inner world of a {age}-year-old. Highly artistic, vector style, crisp lines, zen feeling."

# --- Generate Mandala using DALL·E ---
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
        image_url = response.json()['data'][0]['url']
        return image_url
    else:
        return None

# --- Generate Button ---
if st.button("✨ Create Mandala"):
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key.")
    else:
        prompt = create_prompt(emotion, age)
        with st.spinner("Crafting your mandala..."):
            image_url = generate_image(openai_api_key, prompt)
            if image_url:
                st.image(image_url, caption=f"Mandala for '{emotion}' at age {age}", use_column_width=True)
                st.session_state.history.append((prompt, image_url))
            else:
                st.error("❌ Failed to generate image. Check your API key or quota.")

# --- History Section ---
if st.session_state['history']:
    st.markdown("---")
    st.subheader("🖼️ Your Past Mandalas")
    for i, (p, url) in enumerate(reversed(st.session_state['history'])):
        with st.expander(f"Mandala #{len(st.session_state['history']) - i}"):
            st.image(url, caption=p, use_column_width=True)
