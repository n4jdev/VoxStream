import streamlit as st
import requests
import base64
import time
import io
from audio_effects import apply_audio_effects

# Streamlit app title
st.title("StreamSpeak: Real-time TTS App with Audio Effects")

# Text input
text_input = st.text_area("Enter text to convert to speech:", "Hello, welcome to StreamSpeak!")

# Voice selection
voice = st.selectbox("Select voice:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

# Speed slider
speed = st.slider("Speech speed:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# Audio effects toggle
apply_effects = st.checkbox("Apply human-like microphone effects")

# API endpoint
API_URL = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"

# API headers
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json",
    "authority": "europe-west3-bubble-io-284016.cloudfunctions.net",
    "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
    "authorization": "Bearer dc22c6f09ef2fa3d96a53b589ecc2b5a644db8fb24bbd21dac77370017fb792208e358d5df25bb1f2669304fb7bbd5f3f08119079044421acf8e0663667a573f03606155273cb02a2a62d9b310a5c2d49fef56b45c59ed6f4e06cc0b31e91f1ba96f364ab6f350ef30d3c4c7e88c09b44ed889ee2e3b09646c7855c3f43272d82a13ff0bbbd5a88b54dc312f60bfaa3a9931e10a47b4cbb8b4be78c687757ee6855d030f836622b9dc8e062dcccaa9601a96c52fe3528be876ed6ed4bc193e1448e96518569bcf98e509df22effed1ed1a405c29438fb3af307281d8416f84146244d7e9b8f58f5af35f6c5b8ee1c2ef5f3e271ec49849704b6d0272f3f709e550db9c3c158f3f18851a9d4cab008c87eac57c04f3d9d899ced500998d0d61e35b691642",
    "origin": "https://openaitexttospeechdemo.bubbleapps.io",
    "referer": "https://openaitexttospeechdemo.bubbleapps.io/",
}

def stream_audio(text):
    payload = {
        "model": "tts-1-hd",
        "input": text,
        "voice": voice,
        "format": "mp3",
        "speed": speed
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=4096)
    except requests.RequestException as e:
        st.error(f"Error: {str(e)}")
        return None

# Always display the audio player
audio_player = st.empty()
audio_player.audio("data:audio/mp3;base64,", format="audio/mp3")

# Generate button
if st.button("Generate Speech"):
    if text_input:
        # Stream the audio
        audio_stream = stream_audio(text_input)
        
        if audio_stream:
            audio_data = b""
            
            for chunk in audio_stream:
                audio_data += chunk
            
            if apply_effects:
                # Apply audio effects
                audio_data = apply_audio_effects(audio_data)
            
            # Update the audio player with the final data
            audio_base64 = base64.b64encode(audio_data).decode()
            audio_player.audio(f"data:audio/mp3;base64,{audio_base64}", format="audio/mp3")
            
            # Provide download link
            st.download_button(
                label="Download Audio",
                data=audio_data,
                file_name="generated_speech.mp3",
                mime="audio/mp3"
            )
    else:
        st.warning("Please enter some text to convert to speech.")

# Footer
st.markdown("---")
st.markdown("StreamSpeak - Powered by Streamlit and Custom TTS API with Audio Effects")
