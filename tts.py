import streamlit as st
import requests
import base64
import time
import json

# Streamlit app title
st.set_page_config(page_title="StreamSpeak: Real-time TTS App", page_icon="🎙️")
st.title("StreamSpeak: Real-time TTS App")

# Text input
text_input = st.text_area("Enter text to convert to speech:", "Hello, welcome to StreamSpeak!")

# Voice selection (currently only Onyx is available)
voice = st.selectbox("Select voice:", ["onyx"])

# Language selection (currently only Filipino/Tagalog is available)
language = st.selectbox("Select language:", ["tl"])

# Speed slider
speed = st.slider("Speech speed:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

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
        "language": language,
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

# Create a placeholder for the audio player
audio_player = st.empty()

# Initialize session state for audio data if it doesn't exist
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = b""

# Function to update audio player
def update_audio_player():
    audio_base64 = base64.b64encode(st.session_state.audio_data).decode()
    audio_player.markdown(f'<audio id="audio-player" src="data:audio/mp3;base64,{audio_base64}" controls>Your browser does not support the audio element.</audio>', unsafe_allow_html=True)

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
        audio_stream = stream_audio(text_input)
        
        if audio_stream:
            start_time = time.time()
            
            for chunk in audio_stream:
                st.session_state.audio_data += chunk
                
                # Update the audio player with the current data
                audio_base64 = base64.b64encode(st.session_state.audio_data).decode()
                st.session_state.current_audio_data = audio_base64
                
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
                mime="audio/mp3"
            )
            
            # Update the audio player one last time
            update_audio_player()
            
            # Add JavaScript to start playing the audio and handle updates
            st.markdown("""
                <script>
                    const audioPlayer = document.getElementById('audio-player');
                    
                    function updateAudioSource(base64Data) {
                        const currentTime = audioPlayer.currentTime;
                        const wasPlaying = !audioPlayer.paused;
                        audioPlayer.src = `data:audio/mp3;base64,${base64Data}`;
                        audioPlayer.load();
                        audioPlayer.currentTime = currentTime;
                        if (wasPlaying) {
                            audioPlayer.play();
                        }
                    }
                    
                    function checkForUpdates() {
                        fetch('_stcore/stream')
                            .then(response => response.json())
                            .then(data => {
                                if (data.current_audio_data) {
                                    updateAudioSource(data.current_audio_data);
                                }
                            });
                    }
                    
                    setInterval(checkForUpdates, 1000);
                </script>
            """, unsafe_allow_html=True)
    else:
        st.warning("Please enter some text to convert to speech.")

# App instructions
st.markdown("""
## How to use StreamSpeak:
1. Enter the text you want to convert to speech in the text area.
2. Select the desired voice (currently only Onyx is available).
3. Choose the language (currently only Filipino/Tagalog is supported).
4. Adjust the speech speed using the slider.
5. Click the "Generate Speech" button.
6. The audio will start playing automatically as it's being generated.
7. You can download the generated audio using the "Download Audio" button.
""")

# Footer
st.markdown("---")
st.markdown("StreamSpeak - Powered by Streamlit and Custom TTS API")
