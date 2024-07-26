import streamlit as st
import requests
import base64
import os
import hashlib

# ElevenLabs API endpoint
API_URL = "https://chatin2.vercel.app/api/elevenlabs"

# Available voices
VOICES = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Sam": "yoZ06aMxZJJ28mfd3POQ"
}

# Cache directory
CACHE_DIR = "voice_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

@st.cache_data
def text_to_speech(text, voice_id):
    # Generate a unique cache key based on the text and voice_id
    cache_key = hashlib.md5(f"{text}:{voice_id}".encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.mp3")

    # Check if the audio is already cached
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return f.read()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'authority': 'chatin2.vercel.app',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://chatin2.vercel.app',
        'referer': 'https://chatin2.vercel.app/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'Cookie': 'uuid=f6c6d909-062f-49bf-8b64-85d9e8374fe0'
    }
    
    data = {
        "data": {
            "voiseId": voice_id,
            "message": text
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        # Cache the audio file
        with open(cache_file, "wb") as f:
            f.write(response.content)
        return response.content
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def get_binary_file_downloader_html(bin_file, file_label='File'):
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}.mp3">Download {file_label}</a>'
    return href

def main():
    st.set_page_config(page_title="VoxStream: Text-to-Speech Converter", page_icon="🎙️", layout="wide")
    
    st.title("VoxStream: Text-to-Speech Converter")
    st.write("Convert your text to speech using ElevenLabs API")

    col1, col2 = st.columns([2, 1])

    with col1:
        text_input = st.text_area("Enter the text you want to convert to speech:", height=150)
        char_count = len(text_input)
        st.write(f"Character count: {char_count}")

        use_custom_voice = st.checkbox("Use Custom Voice")
        if use_custom_voice:
            voice_id = st.text_input("Enter Custom Voice ID:")
        else:
            voice = st.selectbox("Select a voice:", list(VOICES.keys()))
            voice_id = VOICES[voice]

        if st.button("Generate Speech"):
            if text_input.strip() == "":
                st.warning("Please enter some text to convert.")
            else:
                with st.spinner("Generating speech..."):
                    audio_content = text_to_speech(text_input, voice_id)
                    
                    if audio_content:
                        st.success("Speech generated successfully!")
                        
                        # Play audio
                        st.audio(audio_content, format="audio/mp3")
                        
                        # Download button
                        st.markdown(get_binary_file_downloader_html(audio_content, f"VoxStream_audio"), unsafe_allow_html=True)

    with col2:
        st.subheader("About Custom Voices")
        st.write("""
        To use a custom voice:
        1. Check the "Use Custom Voice" box
        2. Enter your custom voice ID
        3. Generate speech as usual
        
        You can obtain custom voice IDs from your ElevenLabs account.
        """)

    # Display cache info
    st.sidebar.title("Cache Information")
    cache_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in os.listdir(CACHE_DIR))
    st.sidebar.write(f"Cache size: {cache_size / 1024 / 1024:.2f} MB")
    if st.sidebar.button("Clear Cache"):
        for file in os.listdir(CACHE_DIR):
            os.remove(os.path.join(CACHE_DIR, file))
        st.sidebar.success("Cache cleared successfully!")

if __name__ == "__main__":
    main()
