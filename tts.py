import streamlit as st
import requests
import base64
import io
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range

# Streamlit app title
st.title("StreamSpeak: Real-time TTS App with Optional Audio Effects")

# Text input
text_input = st.text_area("Enter text to convert to speech:", "Hello, welcome to StreamSpeak!")

# Voice selection
voice = st.selectbox("Select voice:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

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
        "format": "mp3",
        "speed": speed
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        st.error(f"Error: {str(e)}")
        return None

def apply_audio_effects(audio_data):
    # Load audio data
    audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
    
    # Apply compression
    compressed_audio = compress_dynamic_range(audio, threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
    
    # Apply subtle EQ (boost low-mids, cut highs slightly)
    eq_audio = compressed_audio.low_pass_filter(3000).high_shelf(start_freq=4000, gain=-3.0)
    
    # Add subtle distortion
    def apply_distortion(sample):
        distortion_factor = 1.2
        return max(min(int(sample * distortion_factor), 32767), -32768)
    
    distorted_audio = eq_audio.apply_gain(-3)  # Reduce volume before distortion
    distorted_audio = distorted_audio.map(apply_distortion)
    
    # Add subtle noise
    noise = AudioSegment.silent(duration=len(distorted_audio))
    noise = noise.overlay(AudioSegment.from_mono_audiosegments(
        AudioSegment.silent(duration=len(distorted_audio)).set_frame_rate(44100)
    )).apply_gain(-30)  # Reduce noise volume
    
    final_audio = distorted_audio.overlay(noise)
    
    # Export to mp3
    buffer = io.BytesIO()
    final_audio.export(buffer, format="mp3")
    return buffer.getvalue()

# Always display the audio player
audio_player = st.empty()
audio_player.audio("data:audio/mp3;base64,", format="audio/mp3")

# Generate button
if st.button("Generate Speech"):
    if text_input:
        # Get the audio data
        audio_data = stream_audio(text_input)
        
        if audio_data:
            # Store the original audio data in session state
            st.session_state.original_audio = audio_data
            
            # Update the audio player with the original data
            audio_base64 = base64.b64encode(audio_data).decode()
            audio_player.audio(f"data:audio/mp3;base64,{audio_base64}", format="audio/mp3")
            
            # Show the "Apply Effects" button
            st.session_state.show_effects_button = True
    else:
        st.warning("Please enter some text to convert to speech.")

# Apply Effects button
if st.session_state.get('show_effects_button', False):
    if st.button("Apply Human-like Microphone Effects"):
        if hasattr(st.session_state, 'original_audio'):
            # Apply audio effects
            effected_audio = apply_audio_effects(st.session_state.original_audio)
            
            # Update the audio player with the effected data
            audio_base64 = base64.b64encode(effected_audio).decode()
            audio_player.audio(f"data:audio/mp3;base64,{audio_base64}", format="audio/mp3")
            
            # Update the download button to use the effected audio
            st.download_button(
                label="Download Audio with Effects",
                data=effected_audio,
                file_name="generated_speech_with_effects.mp3",
                mime="audio/mp3"
            )
        else:
            st.warning("Please generate speech first before applying effects.")

# Download button for original audio
if hasattr(st.session_state, 'original_audio'):
    st.download_button(
        label="Download Original Audio",
        data=st.session_state.original_audio,
        file_name="generated_speech_original.mp3",
        mime="audio/mp3"
    )

# Footer
st.markdown("---")
st.markdown("StreamSpeak - Powered by Streamlit and Custom TTS API with Optional Pydub Audio Effects")
