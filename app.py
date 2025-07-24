import streamlit as st
import openai
import os
import base64
from io import BytesIO
from datetime import datetime
import requests

# ---------- STYLES ----------
st.set_page_config(page_title="Mandala Generator", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
        font-family: 'Montserrat', sans-serif;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        color: white;
        background-color: #333;
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
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''

# ---------- FUNCTIONS ----------
def generate_caption(age, mood):
    tone = "muted tones and slow floral layers" if "sad" in mood.lower() or "tired" in mood.lower() else \
           "vibrant colors and blooming symmetry" if "joy" in mood.lower() else \
           "light patterns and playful symmetry" if int(age) < 20 else \
           "earthy hues and balanced geometry"
    return f"Age {age}, feeling {mood.lower()} → {tone}"

def generate_mandala(api_key, age, mood):
    openai.api_key = api_key
    prompt = f"Generate a calming, symmetrical mandala art inspired by the emotional state '{mood}' for someone aged {age}. Focus on symmetry, texture, colors, and emotional healing."
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

def get_image_base64(url):
    image_data = requests.get(url).content
    return base64.b64encode(image_data).decode()

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

# ---------- MAIN APP ----------
st.markdown("<h1 style='text-align:center;'>🌀 Mandala Generator</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown("## 🌈 Enter Details to Generate Mandala")
    with st.form("user_input", clear_on_submit=False):
        api_key = st.text_input("🔑 Enter your OpenAI API key", type="password", placeholder="sk-...", value=st.session_state['api_key'])
        age = st.number_input("📅 Your Age", min_value=5, max_value=100, value=25)
        mood = st.text_input("🌤️ Current Mood", placeholder="e.g. calm, sad, joyful")
        submitted = st.form_submit_button("Generate Mandala 🎨")

        if submitted:
            if not api_key:
                st.error("Please enter your OpenAI API key.")
            elif not mood.strip():
                st.error("Please describe your current mood.")
            else:
                st.session_state['api_key'] = api_key
                with st.spinner("Generating your personalized mandala..."):
                    try:
                        image_url = generate_mandala(api_key, age, mood)
                        caption = generate_caption(age, mood)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.session_state.history.insert(0, {
                            "image_url": image_url,
                            "caption": caption,
                            "timestamp": timestamp,
                            "age": age,
                            "mood": mood
                        })
                        st.success("Mandala generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating image: {e}")

# ---------- CHAT HISTORY ----------
st.markdown("---")
st.markdown("## 🗂️ Your Mandala History")

if len(st.session_state.history) == 0:
    st.info("No mandalas generated yet.")
else:
    for i, entry in enumerate(st.session_state.history):
        with st.expander(f"🌀 {entry['timestamp']} | Age {entry['age']} | Mood: {entry['mood'].capitalize()}", expanded=False):
            st.image(entry["image_url"], caption=entry["caption"], use_column_width=True)
            base64_img = get_image_base64(entry["image_url"])
            b64_link = f"data:image/png;base64,{base64_img}"
            st.markdown(
                f'<a href="{b64_link}" download="mandala_{i+1}.png" class="download-btn">📥 Download Image</a>',
                unsafe_allow_html=True
            )

# ---------- DOWNLOAD CHAT HISTORY ----------
st.markdown("---")
st.download_button("📄 Download Chat History", data=download_chat_history(), file_name="mandala_chat_history.txt", mime="text/plain")
