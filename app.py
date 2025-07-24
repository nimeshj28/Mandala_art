import streamlit as st
from PIL import Image
import requests
import io
import openai
from openai import OpenAI

# Session state to track usage
if 'mandala_history' not in st.session_state:
    st.session_state.mandala_history = []
if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0

# ---------- 🎨 Styling ----------
st.set_page_config(layout="wide", page_title="Mandala Brew", page_icon="🌀")

st.markdown("""
    <style>
    body { background-color: #f3f4f6; }
    .stApp { background: linear-gradient(to right, #f8f9fa, #e3f6f5); }
    textarea, input[type="text"], input[type="number"] {
        background-color: #ffffff !important;
        color: #1f1f1f !important;
        border-radius: 10px;
        font-weight: 500;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    .caption {
        font-size: 14px;
        font-style: italic;
        margin-top: 5px;
        color: #444444;
    }
    .download-button {
        display: flex;
        justify-content: center;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- 🖌️ Header + Sidebar ----------
st.title("🎨 Mandala Brew")

with st.sidebar:
    st.markdown("## ☕ Your Vibes, Your Art")
    api_key = st.text_input("🔐 Enter your OpenAI API key", type="password", help="Your own OpenAI API Key.")
    age = st.number_input("🎂 What's your age?", min_value=1, max_value=100, step=1)
    emotion = st.text_input("😎 How are you vibing today?", placeholder="e.g., happy, anxious, curious...")

    submitted = st.button("✨ Let's Brew!")

# ---------- ⚙️ Generate Mandala Function ----------
def generate_mandala_image(emotion, age, api_key):
    prompt = f"Black and white mandala art representing a {age}-year-old person feeling {emotion}. Hand-drawn, detailed, symmetric, clean background, no text."

    client = OpenAI(api_key=api_key)
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    image_url = response.data[0].url
    image = Image.open(requests.get(image_url, stream=True).raw)
    return image, image_url

# ---------- 📸 Download Button ----------
def get_image_download_button(img, filename="mandala.png"):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return st.download_button(
        label="⬇️",
        data=byte_im,
        file_name=filename,
        mime="image/png",
        key=f"download_{filename}"
    )

# ---------- 🌀 Main Output Area ----------
if submitted and api_key and emotion:
    try:
        st.toast("🎨 Brewing your vibe into a mandala... hang tight!", icon="🫧")
        img, url = generate_mandala_image(emotion, age, api_key)

        # Funky caption
        caption = f"At age {age} and feeling {emotion}, your soul's brewing a vibe of mandala like this — balanced, blooming and full of stories!"

        # Track history
        st.session_state.api_call_count += 1
        st.session_state.mandala_history.append({
            "age": age,
            "emotion": emotion,
            "image": img,
            "caption": caption,
            "url": url
        })

    except Exception as e:
        st.error(f"Oops! Something went wrong: {e}")

# ---------- 🗃️ Chat History ----------
with st.expander("🧾 Your Mandala Gallery", expanded=True):
    st.markdown(f"### You’ve brewed **{st.session_state.api_call_count}** mandalas today 🍵")
    for i, item in reversed(list(enumerate(st.session_state.mandala_history))):
        header = f"🌟 Age {item['age']} — Mood: {item['emotion'].capitalize()}"
        with st.container():
            st.markdown(f"#### {header}")
            st.image(item['image'], use_column_width=True)
            st.markdown(f"<div class='caption'>{item['caption']}</div>", unsafe_allow_html=True)
            with st.container():
                get_image_download_button(item['image'], filename=f"mandala_{i}.png")
            st.markdown("---")
