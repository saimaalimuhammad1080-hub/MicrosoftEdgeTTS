import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Unlimited Voice Studio", page_icon="🗣️", layout="centered")

# --- STYLE ---
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 18px !important;
        line-height: 1.5;
        border-radius: 12px;
        border: 1px solid #ccc;
        height: 300px;
    }
    .stButton button {
        background-color: #000;
        color: white;
        border-radius: 30px;
        height: 55px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    .stButton button:hover {
        background-color: #333;
        color: white;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---

def split_text(text, max_chars=2000):
    """Splits text into chunks safe for the API"""
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

async def generate_chunk(text, voice, rate_str):
    """Generates audio for a single chunk"""
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    # We save to a memory buffer instead of file to be faster
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes

# --- APP UI ---
st.title("🗣️ Free Unlimited Voice Studio")
st.caption("Auto-Chunking Enabled • Long Text Support")

# 1. Text Input
text_input = st.text_area("Script", height=350, placeholder="Paste your long script here...")
st.caption(f"{len(text_input)} chars")

# 2. Settings
with st.expander("⚙️ Voice Settings", expanded=True):
    voice_options = {
        "🇺🇸 Male (Guy)": "en-US-GuyNeural",
        "🇺🇸 Female (Jenny)": "en-US-JennyNeural",
        "🇺🇸 Male (Christopher)": "en-US-ChristopherNeural",
        "🇺🇸 Female (Aria)": "en-US-AriaNeural",
        "🇬🇧 Male (Ryan)": "en-GB-RyanNeural",
        "🇬🇧 Female (Sonia)": "en-GB-SoniaNeural",
        "🇵🇰 Urdu (Asad)": "ur-PK-AsadNeural",
        "🇵🇰 Urdu (Uzma)": "ur-PK-UzmaNeural"
    }
    selected_voice_name = st.selectbox("Choose Voice", list(voice_options.keys()))
    selected_voice_code = voice_options[selected_voice_name]
    
    speed = st.slider("Speed", -50, 50, 0, format="%d%%")
    speed_str = f"{'+' if speed >= 0 else ''}{speed}%"

# 3. Generate Button
if st.button("Generate Audio"):
    if not text_input:
        st.warning("Please enter some text.")
    else:
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # 1. Split Text
            chunks = split_text(text_input, max_chars=1500) # Safe limit per request
            total_chunks = len(chunks)
            final_audio_bytes = b""
            
            # 2. Process Chunks
            for i, chunk in enumerate(chunks):
                if not chunk.strip(): continue
                
                status_text.text(f"Converting part {i+1} of {total_chunks}...")
                progress_bar.progress((i / total_chunks))
                
                # Run Async function in Sync environment
                chunk_audio = asyncio.run(generate_chunk(chunk, selected_voice_code, speed_str))
                final_audio_bytes += chunk_audio
            
            progress_bar.progress(1.0)
            status_text.text("Finalizing...")
            
            # 3. Save Final Output
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            with open(output_path, "wb") as f:
                f.write(final_audio_bytes)
            
            # 4. Success
            st.success("Generation Complete!")
            st.audio(output_path)
            
            with open(output_path, "rb") as f:
                st.download_button("⬇️ Download Full MP3", f, "full_speech.mp3", "audio/mpeg")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Try refreshing the page if the error persists.")
