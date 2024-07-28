import streamlit as st
import asyncio
import os
import re
import time
from playwright.async_api import async_playwright
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from scipy.signal import butter, lfilter
import numpy as np
import base64

# Install Playwright browsers
os.system("playwright install")

# Constants
HOST = 'pi.ai'
CONVERSATIONS_PATH = '/api/conversations'
CHAT_PATH = '/api/chat'
VOICE_PATH = '/api/chat/voice'
SAVE_DIRECTORY = 'temp_audio'

class PhoneCallConverter:
    def __init__(self, noise_level=-35, low_cutoff=300, high_cutoff=3400):
        self.noise_level = noise_level
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff

    def process_audio(self, input_file, output_file):
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_channels(1)
        
        audio = self.add_background_noise(audio)
        audio = self.apply_frequency_filter(audio)
        audio = self.add_distortion(audio)
        audio = self.simulate_connection_issues(audio)
        
        audio.export(output_file, format="mp3")

    def add_background_noise(self, audio):
        noise = WhiteNoise().to_audio_segment(duration=len(audio))
        noise = noise - (noise.dBFS - self.noise_level)
        return audio.overlay(noise)

    def apply_frequency_filter(self, audio):
        samples = np.array(audio.get_array_of_samples())
        nyquist = audio.frame_rate / 2
        low, high = self.low_cutoff / nyquist, self.high_cutoff / nyquist
        b, a = butter(5, [low, high], btype='band')
        filtered_samples = lfilter(b, a, samples)
        return AudioSegment(
            filtered_samples.astype(audio.array_type).tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=1
        )

    def add_distortion(self, audio, amount=0.03):
        samples = np.array(audio.get_array_of_samples())
        distorted_samples = samples * (1 + amount * np.sin(2 * np.pi * np.arange(len(samples)) / len(samples)))
        distorted_samples = np.clip(distorted_samples, -32768, 32767).astype(audio.array_type)
        return AudioSegment(
            distorted_samples.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=1
        )

    def simulate_connection_issues(self, audio):
        chunk_size = 500
        chunks = [audio[i:i+chunk_size] for i in range(0, len(audio), chunk_size)]
        
        for i in range(len(chunks)):
            if np.random.random() < 0.03:
                fade_duration = min(chunk_size // 2, 100)
                chunks[i] = chunks[i].fade_in(fade_duration).fade_out(fade_duration)
                chunks[i] = chunks[i].compress_dynamic_range(threshold=-15, ratio=4.0, attack=5.0, release=50.0)
                chunks[i] = chunks[i] - 6
            elif np.random.random() < 0.01:
                dropout_duration = np.random.randint(10, 50)
                silent_part = AudioSegment.silent(duration=dropout_duration)
                fade_duration = min(dropout_duration // 2, 10)
                chunks[i] = chunks[i][:chunk_size//2-dropout_duration//2] + silent_part.fade_in(fade_duration).fade_out(fade_duration) + chunks[i][chunk_size//2+dropout_duration//2:]
        
        return sum(chunks)

class PiAITTS:
    def __init__(self):
        self.conversation_id = None
        self.phone_call_converter = PhoneCallConverter()
        self.page = None
        self.playwright = None
        self.browser = None

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        context = await self.browser.new_context()
        self.page = await context.new_page()
        await self.page.goto(f"https://{HOST}/talk")

    async def get_conversation_id(self):
        try:
            response = await self.page.evaluate("""
                async () => {
                    const response = await fetch("https://pi.ai/api/conversations", {
                        method: "POST",
                        headers: {
                            "accept": "application/json",
                            "content-type": "application/json"
                        },
                        body: "{}"
                    });
                    return await response.json();
                }
            """)
            
            self.conversation_id = response.get('sid')
            return self.conversation_id
        except Exception as e:
            st.error(f"Error getting conversation ID: {str(e)}")
            return None

    async def send_message(self, message):
        try:
            response = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch("https://pi.ai/api/chat", {{
                        method: "POST",
                        headers: {{
                            "Accept": "text/event-stream",
                            "Content-Type": "application/json",
                            "X-Api-Version": "3"
                        }},
                        body: JSON.stringify({{
                            conversation: "{self.conversation_id}",
                            text: "{message}"
                        }})
                    }});
                    return await response.text();
                }}
            """)

            for line in response.split('\n'):
                if line.startswith('event: received'):
                    received_data = next(line for line in response.split('\n') if line.startswith('data:')).split('data: ')[1]
                    return received_data
            return None
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
            return None

    async def get_voice(self, message_sid, voice_number):
        try:
            voice_response = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch("https://pi.ai/api/chat/voice?mode=eager&voice=voice{voice_number}&messageSid={message_sid}", {{
                        method: "GET",
                        headers: {{
                            "Range": "bytes=0-"
                        }}
                    }});
                    const arrayBuffer = await response.arrayBuffer();
                    return Array.from(new Uint8Array(arrayBuffer));
                }}
            """)

            timestamp = int(time.time())
            filename = f"tts_output_{timestamp}.mp3"
            os.makedirs(SAVE_DIRECTORY, exist_ok=True)
            input_path = os.path.join(SAVE_DIRECTORY, filename)

            with open(input_path, 'wb') as f:
                f.write(bytes(voice_response))

            return input_path

        except Exception as e:
            st.error(f"Error getting voice: {str(e)}")
            return None

async def main():
    st.title("PI.AI TTS App")

    tts = PiAITTS()
    await tts.initialize()
    tts.conversation_id = await tts.get_conversation_id()

    user_input = st.text_area("Enter text to convert to speech:", "Hello, world!")
    voice_number = st.selectbox("Select voice (1-8):", list(range(1, 9)), key="voice_select")
    apply_effects = st.checkbox("Apply phone call effects", key="effects_checkbox")

    if st.button("Generate TTS"):
        with st.spinner("Generating audio..."):
            received_data = await tts.send_message(user_input)
            if received_data:
                received_sid = eval(received_data).get('sid')
                audio_path = await tts.get_voice(received_sid, voice_number)
                if audio_path:
                    if apply_effects:
                        output_path = os.path.join(SAVE_DIRECTORY, f"processed_{os.path.basename(audio_path)}")
                        tts.phone_call_converter.process_audio(audio_path, output_path)
                        os.remove(audio_path)
                        audio_path = output_path
                    
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    
                    audio_base64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'<audio autoplay controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    
                    os.remove(audio_path)
                else:
                    st.error("Failed to generate audio. Please try again.")
            else:
                st.error("Failed to get a response. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
