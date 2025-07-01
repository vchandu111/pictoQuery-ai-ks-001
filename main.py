import streamlit as st
from openai import OpenAI
import base64

# ------------------ CONFIG -------------------

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

st.set_page_config(layout="wide", page_title="Image Q&A Chatbot")
st.title("🧠 Image Q&A Chatbot")

# ------------------ SESSION INIT -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "base64_image" not in st.session_state:
    st.session_state.base64_image = None

# ------------------ LAYOUT -------------------
col1, col2 = st.columns([1, 2])

# ----------- LEFT COLUMN: Image Upload ----------
with col1:
    uploaded_file = st.file_uploader("📤 Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="📷 Your Image", use_column_width=True)
        st.session_state.base64_image = base64.b64encode(image_bytes).decode("utf-8")

# ----------- RIGHT COLUMN: Chat Interface ----------
with col2:
    st.markdown("### 💬 Chat")
    # Show chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**🤖 GPT-4:** {msg['content']}")

    user_input = st.text_input("Ask something about the image")

    if st.button("Send"):
        if not st.session_state.base64_image:
            st.warning("Please upload an image first.")
        elif user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_input},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{st.session_state.base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()  # ✅ Correct method

            except Exception as e:
                st.error(f"❌ Error: {e}")
