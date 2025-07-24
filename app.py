import streamlit as st
import requests
from PIL import Image
from io import BytesIO

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
        background-color: #2d2d3a;
        color: white;
        border-radius: 6px;
        padding: 0.5rem;
        font-size: 16px;
    }
    .stButton>button {
        background-color: #ffffff10;
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

# --- Logo / Fun Sketch ---
st.image("https://i.imgur.com/YZlVgFy.png", width=150)  # Cute sketchy wizard with paintbrush

st.title("🌀 Mandala by Mood")
st.markdown("### ✨ Yo Art Wizard! Ready to summon a sacred circle based on your **feels** and **age vibe**? Let's go!")

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Sidebar for Past Chats ---
with st.sidebar:
    st.header("🧾 Past Mandalas")
    if st.session_state['history']:
        for i, (prompt, url) in enumerate(reversed(st.session_state['history'])):
            st.markdown(f"**Mandala #{len(st.session_state['history']) - i}**")
            st.image(url, caption=prompt, use_container_width=True)
            st.markdown("---")
    else:
        st.info("No art spells yet, wizard.")

# --- User Input ---
st.subheader("🪄 Your Mandala Spell Inputs")
openai_api_key = st.text_input("🔐 Drop Your Secret Spellbook (API Key)", type="password")

col1, col2 = st.columns(2)
with col1:
    age = st.text_input("🎂 Age you're rocking", "25")
with col2:
    emotion = st.text_input("💫 What’s the current vibe?", "peaceful")

# --- Prompt Generator ---
def make_prompt(emotion, age):
    return f"Detailed black and white symmetrical mandala art, inspired by the emotion '{emotion}' and the perspective of a {age}-year-old. Highly artistic, symmetrical, spiritual pattern, zen feeling."

# --- Generate Mandala ---
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

# --- Generate Button ---
if st.button("🎨 Cast the Mandala Spell!"):
    if not openai_api_key:
        st.warning("⚠️ Drop that API key first, wizard!")
    else:
        prompt = make_prompt(emotion, age)
        with st.spinner("✨ Channeling divine patterns..."):
            img_url = generate_image(openai_api_key, prompt)
            if img_url:
                st.image(img_url, caption=f"🧘 Mandala for a {age}-year-old feeling '{emotion}'", use_container_width=True)
                st.session_state.history.append((prompt, img_url))
            else:
                st.error("❌ Spell fizzled. Check your API key or usage.")
