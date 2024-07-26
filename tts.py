import streamlit as st
import requests
import io
from pydub import AudioSegment
from pydub.playback import play
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def text_to_speech(text, voice_id):
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
        return response.content
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def get_binary_file_downloader_html(bin_file, file_label='File'):
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}.mp3">Download {file_label}</a>'
    return href

def main():
    st.set_page_config(page_title="VoxStream: Text-to-Speech Converter", page_icon="🎙️")
    
    st.title("VoxStream: Text-to-Speech Converter")
    st.write("Convert your text to speech using ElevenLabs API")

    text_input = st.text_area("Enter the text you want to convert to speech:", height=150)
    voice = st.selectbox("Select a voice:", list(VOICES.keys()))

    if st.button("Generate Speech"):
        if text_input.strip() == "":
            st.warning("Please enter some text to convert.")
        else:
            with st.spinner("Generating speech..."):
                audio_content = text_to_speech(text_input, VOICES[voice])
                
                if audio_content:
                    st.success("Speech generated successfully!")
                    
                    # Play audio
                    st.audio(audio_content, format="audio/mp3")
                    
                    # Download button
                    st.markdown(get_binary_file_downloader_html(audio_content, f"VoxStream_{voice}"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()