import streamlit as st
import requests
import json
import base64
import time
import uuid

# Streamlit app title
st.title("StreamSpeak: Real-time TTS App")

# Text input
text_input = st.text_area("Enter text to convert to speech:", "Hello, welcome to StreamSpeak!")

# Voice selection
voices = {
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
voice = st.selectbox("Select voice:", list(voices.keys()))

# API endpoint
API_URL = "https://chatin2.vercel.app/api/elevenlabs"

# API headers
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
    "Cookie": f"uuid={uuid.uuid4()}"
}

def stream_audio(text, voice_id):
    payload = {
        "data": {
            "voiseId": voice_id,
            "message": text
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=4096)
    except requests.RequestException as e:
        st.error(f"Error: {str(e)}")
        return None

# Create a placeholder for the audio player
audio_player = st.empty()

# Initialize session state for audio data if it doesn't exist
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = b""

# Function to update audio player
def update_audio_player():
    audio_base64 = base64.b64encode(st.session_state.audio_data).decode()
    audio_player.markdown(f'<audio id="audio-player" src="data:audio/mpeg;base64,{audio_base64}" controls>Your browser does not support the audio element.</audio>', unsafe_allow_html=True)

# Initial audio player (empty)
update_audio_player()

# Generate button
if st.button("Generate Speech"):
    if text_input:
        # Reset audio data
        st.session_state.audio_data = b""
        
        # Create a status message
        status = st.empty()
        
        # Stream the audio
        audio_stream = stream_audio(text_input, voices[voice])
        
        if audio_stream:
            start_time = time.time()
            
            for chunk in audio_stream:
                st.session_state.audio_data += chunk
                
                # Update the audio player with the current data
                update_audio_player()
                
                # Update status message
                elapsed_time = time.time() - start_time
                status.text(f"Streaming audio... {elapsed_time:.2f} seconds")
                
                # Add a small delay to allow for smoother updates
                time.sleep(0.1)
            
            # Final update
            status.text(f"Audio generation complete. Total time: {time.time() - start_time:.2f} seconds")
            
            # Provide download link
            st.download_button(
                label="Download Audio",
                data=st.session_state.audio_data,
                file_name="generated_speech.mp3",
                mime="audio/mpeg"
            )
            
            # Add JavaScript to start playing the audio
            st.markdown("""
                <script>
                    const audioPlayer = document.getElementById('audio-player');
                    audioPlayer.play();
                </script>
            """, unsafe_allow_html=True)
    else:
        st.warning("Please enter some text to convert to speech.")

# App instructions
st.markdown("""
## How to use StreamSpeak:
1. Enter the text you want to convert to speech in the text area.
2. Select the desired voice from the available options.
3. Click the "Generate Speech" button.
4. The audio will start playing automatically as it's being generated.
5. You can download the generated audio using the "Download Audio" button.
""")

# Footer
st.markdown("---")
st.markdown("StreamSpeak - Powered by Streamlit and ElevenLabs API")
