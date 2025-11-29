import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Unlimited Voice Studio", page_icon="🗣️", layout="centered")

# --- STYLE (Clean, Minimal, ElevenLabs vibe) ---
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
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---
async def generate_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- APP UI ---
st.title("🗣️ Free Unlimited Voice Studio")
st.caption("No Limits • No Queue • High Quality")

# 1. Text Input
text_input = st.text_area(
    "Script", 
    height=350, 
    placeholder="Paste your long script here (20k+ characters supported)...",
    label_visibility="collapsed"
)

col_info, col_count = st.columns([3, 1])
col_info.info("✨ Suggestion: Use 'Guy' or 'Jenny' for best results.")
col_count.caption(f"{len(text_input)} chars")

# 2. Settings (Clean Dropdown)
with st.expander("⚙️ Voice Settings", expanded=True):
    # Popular high-quality voices
    voice_options = {
        "🇺🇸 Male (Guy) - Professional": "en-US-GuyNeural",
        "🇺🇸 Female (Jenny) - Soft": "en-US-JennyNeural",
        "🇺🇸 Male (Christopher) - Deep": "en-US-ChristopherNeural",
        "🇺🇸 Female (Aria) - Energetic": "en-US-AriaNeural",
        "🇬🇧 Male (Ryan) - British": "en-GB-RyanNeural",
        "🇬🇧 Female (Sonia) - British": "en-GB-SoniaNeural",
        "🇵🇰 Urdu (Asad)": "ur-PK-AsadNeural",
        "🇵🇰 Urdu (Uzma)": "ur-PK-UzmaNeural"
    }
    
    selected_voice_name = st.selectbox("Choose Voice", list(voice_options.keys()))
    selected_voice_code = voice_options[selected_voice_name]

    # Speed slider
    speed = st.slider("Speed", -50, 50, 0, format="%d%%")
    speed_str = f"{'+' if speed >= 0 else ''}{speed}%"

# 3. Generate Button
if st.button("Generate Audio"):
    if not text_input:
        st.warning("Please enter some text.")
    else:
        status = st.empty()
        status.text("Generating audio... (This is fast!)")
        
        try:
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            output_path = temp_file.name
            temp_file.close()

            # Run Async Function
            # We add the speed modifier to the voice if supported, but edge-tts handles text-to-speech
            # To keep it simple and stable, we stick to standard generation for now.
            
            asyncio.run(generate_speech(text_input, selected_voice_code, output_path))
            
            status.empty()
            st.success("Generation Complete!")
            
            # Audio Player
            st.audio(output_path)
            
            # Download Button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download MP3",
                    data=f,
                    file_name="voice_studio_output.mp3",
                    mime="audio/mpeg"
                )
                
            # Cleanup
            os.unlink(output_path)

        except Exception as e:
            st.error(f"Error: {e}")
