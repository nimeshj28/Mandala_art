import streamlit as st
import openai
import requests
from PIL import Image
import io
import uuid
import base64

# --- App Config ---
st.set_page_config(page_title="Mandala Generator", layout="wide", page_icon="🌀")

# --- Custom CSS ---
st.markdown("""
    <style>
        .download-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #2563eb;
            color: white;
            padding: 8px 14px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
            text-decoration: none;
        }
        .chat-history {
            background-color: #f8fafc;
            padding: 20px;
            border-radius: 12px;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 2px 0 8px rgba(0,0,0,0.05);
        }
        .main-content {
            padding: 20px 40px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Session State ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Helper: Mandala Generation Stub ---
def generate_mandala_image(age, mood):
    prompt = f"mandala art in the style of '{mood}' emotion and {age} years old, peaceful, detailed, symmetric"
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response["data"][0]["url"]
    image = Image.open(requests.get(image_url, stream=True).raw)
    return image

# --- Helper: Caption Generation ---
def generate_caption(mood, age):
    base_caption = {
        "peaceful": "Radiant petals mirror your calm energy.",
        "joyful": "Playful loops to match your vibrant joy.",
        "anxious": "Expanding ripples guide you to center calmly.",
        "tired": "Balanced symmetry gives you space to rest.",
        "focused": "Clean repetition to hold your grounded attention."
    }
    age_note = {
        "teen": "Made with playful curves that echo your curiosity.",
        "adult": "Structured elegance to reflect your calm strength.",
        "senior": "Gentle patterns, paced for clarity and grace."
    }
    age_group = "teen" if age < 20 else "adult" if age < 60 else "senior"
    return f"{base_caption.get(mood, 'A mandala to restore your balance.')} {age_note[age_group]}"

# --- Helper: Download Link ---
def get_image_download_link(img, filename="mandala.png"):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    b64 = base64.b64encode(byte_im).decode()
    return f'<a href="data:file/png;base64,{b64}" download="{filename}" class="download-btn">Download</a>'

# --- Layout Columns: Left Chat, Right Generator ---
col1, col2 = st.columns([1.2, 3])

# --- LEFT: Chat History Panel ---
with col1:
    st.markdown("## 🧘 Mandala Journal", unsafe_allow_html=True)
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"🌀 Mandala {idx+1}", expanded=False):
            st.image(item["image"], width=200)
            st.markdown(f"**🪷 Caption:** {item['caption']}")
            st.markdown(get_image_download_link(item["image"], f"mandala_{idx+1}.png"), unsafe_allow_html=True)

    if st.session_state.history:
        def download_chat_history():
            history_text = ""
            for i, item in enumerate(st.session_state.history):
                history_text += f"Mandala {i+1}:\nCaption: {item['caption']}\n\n"
            return history_text.encode()

        st.download_button("📥 Download All Captions", data=download_chat_history(),
                           file_name="mandala_journal.txt", mime="text/plain")

    st.markdown('</div>', unsafe_allow_html=True)

# --- RIGHT: Mandala Generator ---
with col2:
    st.markdown("<h1 style='margin-top: -10px;'>Mandala Generator 🌀</h1>", unsafe_allow_html=True)
    st.markdown("Crafted uniquely for your mood and age.")

    with st.form("mandala_form"):
        age = st.slider("Your Age", 10, 80, 25)
        mood = st.selectbox("Current Mood", ["peaceful", "joyful", "anxious", "tired", "focused"])
        submit = st.form_submit_button("✨ Create Mandala")

    if submit:
        with st.spinner("Drawing your mandala..."):
            mandala_img = generate_mandala_image(age, mood)
            caption = generate_caption(mood, age)
            st.session_state.history.insert(0, {
                "id": str(uuid.uuid4()),
                "image": mandala_img,
                "caption": caption
            })

    # Latest Mandala Display
    if st.session_state.history:
        st.markdown("### 🌸 Latest Mandala")
        latest = st.session_state.history[0]
        col_img, col_text = st.columns([1.5, 2])
        with col_img:
            st.image(latest["image"], use_column_width=True)
            st.markdown(get_image_download_link(latest["image"], "latest_mandala.png"), unsafe_allow_html=True)
        with col_text:
            st.markdown(f"**Your Caption:** {latest['caption']}")
