import streamlit as st
import openai
import base64
import requests
from io import BytesIO
from PIL import Image
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mandala Mood Brewer", layout="wide", page_icon="🌀")

# --- STYLES ---
custom_css = """
<style>
body {
    background-color: #f8f0ff;
    font-family: 'Segoe UI', sans-serif;
}
input, textarea {
    background-color: #fff9f5 !important;
    color: #333 !important;
}
.stTextInput input, .stNumberInput input {
    border-radius: 8px;
    padding: 10px;
    font-size: 16px;
}
.stButton>button {
    background-color: #6a0dad;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 18px;
}
.stButton>button:hover {
    background-color: #8a2be2;
}
.download-icon {
    display: block;
    text-align: center;
    margin-top: 5px;
}
.expander-header {
    font-weight: bold;
    font-size: 18px;
    color: #5e4b8b;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SIDEBAR HISTORY ---
st.sidebar.title("🗂️ Your Mandala History")

if 'history' not in st.session_state:
    st.session_state.history = []

for i, entry in enumerate(reversed(st.session_state.history)):
    with st.sidebar.expander(f"🌟 Age {entry['age']} – {entry['emotion'].capitalize()}", expanded=False):
        st.image(entry['image'], use_column_width=True)
        st.caption(entry['caption'])

# --- MAIN UI ---
st.title("🎨 Mandala Mood Brewer")
st.subheader("Drop your vibes, and let's brew some cosmic art!")

# --- INPUTS ---
with st.form("mandala_form"):
    api_key = st.text_input("🔑 Drop your OpenAI API key here (we don't store it)", type="password")
    emotion = st.text_input("🧠 What’s your current mood?", max_chars=30)
    age = st.number_input("📅 How young are you feeling today?", min_value=1, max_value=120, step=1)
    submitted = st.form_submit_button("✨ Let's Brew")

# --- UTILITIES ---
def generate_mandala_image(emotion, age, api_key):
    prompt = f"Black and white mandala art inspired by a {age}-year-old person feeling {emotion}. Artistic, elegant, intricate, symmetric, circular, hand-drawn style. No text, no watermark, no background, only art."
    openai.api_key = api_key

    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    image = Image.open(requests.get(image_url, stream=True).raw)
    return image, image_url

def get_caption(emotion, age):
    if age < 18:
        tone = "playful and full of energy"
    elif 18 <= age <= 30:
        tone = "exploring the world, balancing ambition and joy"
    elif 31 <= age <= 45:
        tone = "mature and responsible, with bursts of creativity"
    else:
        tone = "wise, reflective, and deeply centered"

    return f"Age {age} and mood '{emotion}' — this mandala reflects a {tone} vibe. Each swirl mirrors your emotional frequency."

def image_to_bytes(image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

def get_image_download_link(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:file/png;base64,{b64}" download="mandala.png"><img src="https://cdn-icons-png.flaticon.com/512/109/109612.png" width="25"/></a>'

# --- GENERATE IMAGE ---
if submitted:
    if not api_key or not emotion:
        st.error("Please enter both your API key and your mood.")
    else:
        with st.spinner("✨ Brewing your mandala..."):
            try:
                image, image_url = generate_mandala_image(emotion, age, api_key)
                caption = get_caption(emotion, age)

                st.image(image, caption=caption, use_column_width=True)
                st.markdown(get_image_download_link(image), unsafe_allow_html=True)

                # Save in chat-like history
                st.session_state.history.append({
                    "age": age,
                    "emotion": emotion,
                    "image": image,
                    "caption": caption
                })

            except Exception as e:
                st.error(f"Oops! Something went wrong: {e}")
