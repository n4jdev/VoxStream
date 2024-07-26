import streamlit as st
import requests
import json
import time

def stream_audio(url, headers, data):
    with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk

st.title("ElevenLabs Streaming Audio App")

message = st.text_input("Enter your message:", "Hello there")
voice_id = st.text_input("Enter voice ID:", "pNInz6obpgDQGcFmaJgB")

if st.button("Generate Audio"):
    url = "https://chatin2.vercel.app/api/elevenlabs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "authority": "chatin2.vercel.app",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "content-type": "text/plain;charset=UTF-8",
        "origin": "https://chatin2.vercel.app",
        "referer": "https://chatin2.vercel.app/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Cookie": "uuid=f6c6d909-062f-49bf-8b64-85d9e8374fe0"
    }
    data = {
        "data": {
            "voiseId": voice_id,
            "message": message
        }
    }

    audio_placeholder = st.empty()
    status_placeholder = st.empty()

    status_placeholder.text("Generating audio...")
    audio_data = b""
    for chunk in stream_audio(url, headers, data):
        audio_data += chunk
        status_placeholder.text(f"Received {len(audio_data)} bytes...")

    status_placeholder.text("Audio generation complete!")
    audio_placeholder.audio(audio_data, format="audio/mpeg", start_time=0)

st.write("Note: This app streams the audio response from the ElevenLabs API.")
