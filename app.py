import streamlit as st
import openai
from openai import OpenAI
from PIL import Image
import io
import requests

# --- Init ---
st.set_page_config(page_title="Mandala Brew", layout="wide")

if 'mandala_history' not in st.session_state:
    st.session_state.mandala_history = []
if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0
if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = True

# --- CSS Styling ---
st.markdown("""
    <style>
    body { background-color: #f6f7fb; }
    .stApp {
        background: linear-gradient(to right, #f1f5f9, #e3f2fd);
        font-family: 'Segoe UI', sans-serif;
    }
    textarea, input[type="text"], input[type="number"] {
        background-color: #ffffff !important;
        color: #111 !important;
        border-radius: 10px;
        font-weight: 500;
    }
    .mandala-img-container {
        position: relative;
        display: inline-block;
    }
    .download-btn {
        position: absolute;
        bottom: 15px;
        right: 15px;
        background-color: #3b82f6;
        border: none;
        padding: 10px;
        border-radius: 50%;
        cursor: pointer;
        z-index: 10;
    }
    .caption {
        font-size: 15px;
        font-style: italic;
        margin-top: 10px;
        color: #333333;
    }
    .sidebar-toggle {
        font-weight: bold;
        color: #2563eb;
        cursor: pointer;
    }
    .chat-history {
        height: 100vh;
        overflow-y: auto;
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Functions ---
def generate_mandala_image(emotion, age, api_key):
    prompt = f"Black and white hand-drawn mandala art representing a {age}-year-old feeling {emotion}. Clean, symmetrical, artistic, detailed line work, no color, no text."
    client = OpenAI(api_key=api_key)

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    image = Image.open(requests.get(image_url, stream=True).raw)
    return image, image_url

def get_caption(age, emotion):
    templates = {
        "happy": f"At age {age}, happiness feels like sweet wind in the best climate — this mandala radiates balance from every direction.",
        "engaged": f"Age {age} with an engaged mind — petals rooted in purpose, showing a responsible soul anchoring life's leaves.",
        "curious": f"{age} and curious — this mandala swirls like questions echoing in a hungry mind.",
        "peaceful": f"{age} years of peace — symmetry like still waters, calm and quietly wise.",
        "tired": f"Feeling tired at {age}? This mandala holds soft repetition, reflecting the weight and rhythm of effort."
    }
    return templates.get(emotion.lower(), f"This art reflects how a {age}-year-old feeling {emotion} uniquely blooms — patterns mirroring your vibe.")

def get_image_download_button(img, filename):
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

# --- Left Sidebar (Chat-like) ---
with st.sidebar:
    st.markdown("### 🧾 Your Mandala Gallery")
    if st.button("🔽 Toggle Chat History"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

    if st.session_state.show_sidebar:
        for i, item in enumerate(reversed(st.session_state.mandala_history)):
            tag = f"{item['age']} • {item['emotion'].capitalize()}"
            st.image(item['image'].resize((60, 60)), caption=tag, use_column_width=False)
            if st.button(f"🗂️ {tag}", key=f"view_{i}"):
                st.session_state.selected = len(st.session_state.mandala_history) - 1 - i

# --- Centered Input Layout ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("## 🎨 Mandala Brew")
    st.markdown("Let’s vibe and draw your soul ✨")

    api_key = st.text_input("🔐 Your OpenAI API Key", type="password", placeholder="Paste here")
    age = st.number_input("🎂 Your Age", min_value=5, max_value=100, step=1)
    emotion = st.text_input("🧠 Your Mood", placeholder="e.g. happy, curious, peaceful...")

    if st.button("🌈 Let’s Brew"):
        if api_key and age and emotion:
            st.toast("Brewing your mandala with DALL·E 3 🌀", icon="🪄")
            try:
                img, url = generate_mandala_image(emotion, age, api_key)
                caption = get_caption(age, emotion)

                # Save to history
                st.session_state.api_call_count += 1
                st.session_state.mandala_history.append({
                    "age": age,
                    "emotion": emotion,
                    "image": img,
                    "caption": caption,
                    "url": url
                })
            except Exception as e:
                st.error(f"Something went wrong! 😢\n\n{e}")
        else:
            st.warning("Please enter all fields.")

# --- Main Display: Most Recent Mandala ---
if st.session_state.mandala_history:
    last = st.session_state.mandala_history[-1]
    st.markdown(f"### 🧘 Mandala for Age {last['age']} — {last['emotion'].capitalize()}")

    with st.container():
        # Art + Download button overlay
        col = st.columns([1, 6, 1])[1]
        with col:
            st.image(last['image'], use_column_width=True)
            get_image_download_button(last['image'], filename="your_mandala.png")
            st.markdown(f"<div class='caption'>{last['caption']}</div>", unsafe_allow_html=True)
