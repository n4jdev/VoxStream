import streamlit as st
import requests
import json
import time
import io

def stream_audio(url, headers, data):
    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk

st.title("OpenAI TTS Streaming App")

message = st.text_area("Enter your message:", "Hello, how are you today?")
voice = st.selectbox("Select voice:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
language = st.text_input("Enter language code:", "en")
speed = st.slider("Select speed:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

if st.button("Generate Audio"):
    url = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "authority": "europe-west3-bubble-io-284016.cloudfunctions.net",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "authorization": "Bearer dc22c6f09ef2fa3d96a53b589ecc2b5a644db8fb24bbd21dac77370017fb792208e358d5df25bb1f2669304fb7bbd5f3f08119079044421acf8e0663667a573f03606155273cb02a2a62d9b310a5c2d49fef56b45c59ed6f4e06cc0b31e91f1ba96f364ab6f350ef30d3c4c7e88c09b44ed889ee2e3b09646c7855c3f43272d82a13ff0bbbd5a88b54dc312f60bfaa3a9931e10a47b4cbb8b4be78c687757ee6855d030f836622b9dc8e062dcccaa9601a96c52fe3528be876ed6ed4bc193e1448e96518569bcf98e509df22effed1ed1a405c29438fb3af307281d8416f84146244d7e9b8f58f5af35f6c5b8ee1c2ef5f3e271ec49849704b6d0272f3f709e550db9c3c158f3f18851a9d4cab008c87eac57c04f3d9d899ced500998d0d61e35b691642",
        "origin": "https://openaitexttospeechdemo.bubbleapps.io",
        "referer": "https://openaitexttospeechdemo.bubbleapps.io/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site"
    }
    data = {
        "model": "tts-1-hd",
        "input": message,
        "voice": voice,
        "language": language,
        "format": "mp3",
        "speed": speed
    }

    audio_placeholder = st.empty()
    status_placeholder = st.empty()

    # Create a BytesIO object to store the audio data
    audio_buffer = io.BytesIO()

    # Display the audio player immediately
    audio_player = audio_placeholder.audio(audio_buffer, format="audio/mpeg", start_time=0)

    status_placeholder.text("Generating audio...")
    for chunk in stream_audio(url, headers, data):
        audio_buffer.write(chunk)
        # Update the audio player with the new data
        audio_player.audio(audio_buffer, format="audio/mpeg", start_time=0)
        status_placeholder.text(f"Received {audio_buffer.tell()} bytes...")
        time.sleep(0.1)  # Small delay to allow for smoother updates

    status_placeholder.text("Audio generation complete!")

st.write("Note: This app streams the audio response from the OpenAI TTS API in real-time.")
