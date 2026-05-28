import streamlit as st
import requests
import whisper
import os
from streamlit_mic_recorder import mic_recorder
from static_ffmpeg import add_paths
from pyngrok import ngrok

# =========================
# FFmpeg fix
# =========================
add_paths()

# =========================
# NGROK (FIXED)
# =========================
if "public_url" not in st.session_state:

    public_url = ngrok.connect(8501).public_url
    st.session_state.public_url = public_url

public_url = st.session_state.public_url

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Demeu AI", page_icon="🌿", layout="centered")

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.stApp { background-color: #FAFAFA; }

[data-testid="stSidebar"] {
    background-color: #E0E0E0 !important;
}

.stButton>button {
    background: linear-gradient(90deg, #FF9A9E 0%, #A18CD1 100%) !important;
    color: white !important;
    border-radius: 20px !important;
}

h1 {
    text-align: center;
    background: linear-gradient(to right, #FF7E5F, #86A8E7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

[data-testid="stChatMessage"] {
    background-color: white;
    border-radius: 15px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# MODEL
# =========================
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

# =========================
# STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "trust_contact" not in st.session_state:
    st.session_state.trust_contact = {"name": "", "phone": ""}

# =========================
# AI (OLLAMA)
# =========================
def get_ai_response(prompt):
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": f"Ты Demeu — добрый психолог-друг. Ответь кратко: {prompt}",
                "stream": False
            }
        )
        return r.json().get("response", "Нет ответа")
    except Exception as e:
        return f"Ошибка: {e}"

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("🌿 Настройки")

    st.session_state.trust_contact["name"] = st.text_input("Имя близкого")
    st.session_state.trust_contact["phone"] = st.text_input("Телефон")

    st.header("🎙 Голос")

    audio = mic_recorder(
        start_prompt="🎙 Запись",
        stop_prompt="⏹ Стоп",
        key="mic"
    )

    mood = st.select_slider(
        "Настроение",
        ["Ужасно", "Плохо", "Нормально", "Хорошо", "Отлично"],
        value="Нормально"
    )

# =========================
# MAIN
# =========================
st.title("🌿 Demeu AI")

# FIX: ngrok link
st.info(f"🌍 NGROK: {public_url}")

# =========================
# CHAT INPUT
# =========================
prompt = st.chat_input("Напиши сообщение...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Demeu думает..."):
        response = get_ai_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})

# =========================
# VOICE INPUT
# =========================
if audio:

    temp_file = "temp.wav"

    with open(temp_file, "wb") as f:
        f.write(audio["bytes"])

    try:
        text = model.transcribe(temp_file)["text"]

        st.session_state.messages.append({"role": "user", "content": f"🎤 {text}"})

        with st.spinner("Думаю..."):
            response = get_ai_response(text)

        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"Ошибка: {e}")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# =========================
# SHOW CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# ALERT
# =========================
if mood == "Ужасно":
    st.error(
        f"⚠️ Свяжись с: {st.session_state.trust_contact['name']} "
        f"{st.session_state.trust_contact['phone']}"
    )