import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64
import random

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #000000, #1c1c1c);
        color: white;
    }

    textarea, input[type="text"], input[type="number"] {
        background-color: #222222 !important;
        color: #ffffff !important;
        border-radius: 10px;
        font-weight: 500;
        padding: 10px;
        border: 1px solid #444;
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
        color: #dddddd;
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
    }

    .sidebar .block-container {
        background-color: #111111;
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

# --- Session State Setup ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- Sidebar Chat History ---
with st.sidebar:
    st.title("🌀 Mandala History")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"🎯 {item['age']} | {item['emotion']}", expanded=False):
                st.image(item['image'], caption=item['caption'], use_container_width=True)
    else:
        st.markdown("No mandalas brewed yet!")

# --- Main Title & Input Area ---
st.title("🎨 Mandala Mood Crafter")
st.markdown("Let's blend **emotion + age** into stunning black-and-white mandalas 🖤")

with st.form("user_input_form"):
    user_api = st.text_input("🔐 Enter your OpenAI API key:")
    age = st.number_input("🎂 Your age:", min_value=1, max_value=120, step=1)
    mood = st.text_input("💭 How are you feeling? (1 word)")

    submit = st.form_submit_button("✨ Let's Brew!")

# --- Caption Generator ---
def generate_caption(age, mood):
    samples = [
        f"Age {age}, feeling {mood} — a symphony of balance shaped in sacred geometry.",
        f"{age} and {mood}? This art is the sweet wind in your best season — flowing from all four corners.",
        f"At {age}, being {mood} means petals hold stories of now and next — this mandala channels that energy.",
        f"{mood.capitalize()} at {age} is a phase of layers — this piece folds and unfolds just like life.",
        f"This mandala reflects your {mood} spirit at {age}, where symmetry meets spark."
    ]
    return random.choice(samples)

# --- Image Generator ---
def generate_mandala(api_key, age, mood):
    client = OpenAI(api_key=api_key)
    prompt = f"A beautiful, detailed, symmetrical black and white mandala that represents a {mood} person aged {age}. Intricate lines, artistic symmetry, circular balance, spiritual abstract design, centered geometry."
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    return image_url

# --- Main Execution ---
if submit and user_api and age and mood:
    try:
        with st.spinner("🎨 Brewing your mandala..."):
            image_url = generate_mandala(user_api, age, mood)
            st.session_state.count += 1
            caption = generate_caption(age, mood)

            # Downloadable image
            image_bytes = BytesIO()
            image_response = Image.open(BytesIO(requests.get(image_url).content))
            image_response.save(image_bytes, format='PNG')
            b64 = base64.b64encode(image_bytes.getvalue()).decode()

            st.markdown(f"""
                <div style="position: relative;">
                    <img src="{image_url}" style="width: 100%; border-radius: 8px;" />
                    <a href="data:file/png;base64,{b64}" download="mandala.png">
                        <button class="download-btn">⬇️</button>
                    </a>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p class='caption'>{caption}</p>", unsafe_allow_html=True)

            # Add to history
            st.session_state.history.insert(0, {
                'age': age,
                'emotion': mood,
                'caption': caption,
                'image': image_response
            })

            st.success(f"Mandala brewed successfully! Total images generated this session: {st.session_state.count}")
    except Exception as e:
        st.error(f"Oops! Something went wrong: {str(e)}")
