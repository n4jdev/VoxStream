import streamlit as st
import requests
import io
from pydub import AudioSegment
from pydub.playback import play

# Streamlit app configuration
st.set_page_config(page_title="StreamSpeak: Instant TTS Audio Streamer", page_icon="🎙️")

# Constants
API_URL = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"
AUTH_TOKEN = "dc22c6f09ef2fa3d96a53b589ecc2b5a644db8fb24bbd21dac77370017fb792208e358d5df25bb1f2669304fb7bbd5f3f08119079044421acf8e0663667a573f03606155273cb02a2a62d9b310a5c2d49fef56b45c59ed6f4e06cc0b31e91f1ba96f364ab6f350ef30d3c4c7e88c09b44ed889ee2e3b09646c7855c3f43272d82a13ff0bbbd5a88b54dc312f60bfaa3a9931e10a47b4cbb8b4be78c687757ee6855d030f836622b9dc8e062dcccaa9601a96c52fe3528be876ed6ed4bc193e1448e96518569bcf98e509df22effed1ed1a405c29438fb3af307281d8416f84146244d7e9b8f58f5af35f6c5b8ee1c2ef5f3e271ec49849704b6d0272f3f709e550db9c3c158f3f18851a9d4cab008c87eac57c04f3d9d899ced500998d0d61e35b691642"

# Helper function to stream audio
def stream_audio(response):
    buffer = io.BytesIO()
    for chunk in response.iter_content(chunk_size=4096):
        buffer.write(chunk)
    buffer.seek(0)
    return AudioSegment.from_mp3(buffer)

# Function to generate and play audio
def generate_and_play_audio(text, voice, language, speed):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "authorization": f"Bearer {AUTH_TOKEN}",
        "origin": "https://openaitexttospeechdemo.bubbleapps.io",
        "referer": "https://openaitexttospeechdemo.bubbleapps.io/"
    }
    
    payload = {
        "model": "tts-1-hd",
        "input": text,
        "voice": voice,
        "language": language,
        "format": "mp3",
        "speed": speed
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        
        audio = stream_audio(response)
        st.audio(audio.export(format="mp3").read(), format="audio/mp3", start_playing=True)
        st.success("Audio generated and playing!")
    except requests.RequestException as e:
        st.error(f"An error occurred: {str(e)}")

# Streamlit app
def main():
    st.title("StreamSpeak: Instant TTS Audio Streamer")
    st.write("Convert text to speech and listen instantly!")

    # Text input
    text_input = st.text_area("Enter the text you want to convert to speech:", height=150)

    # Voice selection
    voice_options = ["onyx", "alloy", "echo", "fable", "nova", "shimmer"]
    selected_voice = st.selectbox("Select a voice:", voice_options)

    # Language selection
    language_options = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "ko", "tl"]
    selected_language = st.selectbox("Select a language:", language_options)

    # Speed selection
    speed = st.slider("Speech speed:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    # Automatically generate and play audio when text is entered
    if text_input:
        generate_and_play_audio(text_input, selected_voice, selected_language, speed)

    st.markdown("---")
    st.write("Note: This application uses AI-generated voices. The audio you hear is not a human voice.")

if __name__ == "__main__":
    main()
