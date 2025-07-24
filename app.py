import streamlit as st
from PIL import Image
import openai
import requests
import base64
import io

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background-color: #1a1a1a;
        color: #f5f5f5;
    }

    textarea, input[type="text"], input[type="number"] {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border-radius: 10px;
        font-weight: 500;
        padding: 10px;
        border: 1px solid #555;
    }

    label {
        color: #eeeeee !important;
    }

    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 8px 16px;
    }

    .caption {
        font-size: 16px;
        font-style: italic;
        color: #cccccc;
        margin-top: 10px;
    }

    .download-btn {
        background-color: #3b82f6;
        border: none;
        padding: 10px;
        border-radius: 50%;
        position: absolute;
        bottom: 15px;
        right: 15px;
        z-index: 10;
        text-decoration: none;
        font-size: 20px;
        color: white;
    }

    .sidebar .block-container {
        background-color: #242424;
    }

    .chat-history {
        font-size: 14px;
        color: #cccccc;
    }

    .sidebar-icon {
        border-left: 3px solid #3b82f6;
        padding-left: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Chat History ---
with st.sidebar:
    st.title("🎨 Past Mandalas")
    for idx, chat in enumerate(st.session_state.chat_history):
        with st.expander(f"🌀 {chat['age']} | {chat['emotion'].capitalize()}"):
            st.image(chat["image"], caption=chat["caption"], use_container_width=True)

# --- Main Input UI ---
st.markdown("## 🧘 Brew Your Mandala")
st.markdown("How’s your vibe today? Drop your **mood** and **age**, and we’ll sketch the feeling ✨")

api_key = st.text_input("🔐 Your OpenAI API Key", type="password")
age = st.number_input("🎂 Your Age", min_value=5, max_value=100, step=1)
emotion = st.text_input("💭 Your Mood (e.g. peaceful, excited, nostalgic)")

if st.button("☕ Let’s Brew"):
    if not api_key or not emotion or not age:
        st.warning("Please fill all fields to get your mandala ☝️")
    else:
        openai.api_key = api_key
        with st.spinner("Creating your artistic aura..."):
            prompt = f"Black and white line art mandala symbolizing {emotion} emotion for a {age}-year-old person. Highly detailed, symmetrical, spiritual tone."

            try:
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    n=1
                )
                image_url = response.data[0].url
                img_data = requests.get(image_url).content
                image = Image.open(io.BytesIO(img_data))

                # --- Generate Caption ---
                caption = f"Age {age}, feeling {emotion} – this mandala reflects your moment. Like petals stretching from all directions, your energy is balanced and expressive."

                # --- Save to Chat History ---
                st.session_state.chat_history.append({
                    "age": age,
                    "emotion": emotion,
                    "caption": caption,
                    "image": image
                })

                # --- Display Output ---
                st.image(image, caption=caption, use_container_width=True)

                # --- Download Button ---
                b64 = base64.b64encode(img_data).decode()
                dl_link = f'<a href="data:image/png;base64,{b64}" download="mandala_{age}_{emotion}.png" class="download-btn">⬇️</a>'
                st.markdown(dl_link, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
