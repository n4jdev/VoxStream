import streamlit as st
import subprocess
import json
import io
import re

def execute_chat_curl(user_input):
    curl_command = [
        'curl', '-X', 'POST', 'https://pi.ai/api/chat',
        '-H', 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        '-H', 'Accept: text/event-stream',
        '-H', 'Content-Type: application/json',
        '-H', 'authority: pi.ai',
        '-H', 'accept-language: en-PH,en-US;q=0.9,en;q=0.8',
        '-H', 'origin: https://pi.ai',
        '-H', 'referer: https://pi.ai/talk',
        '-H', 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"',
        '-H', 'sec-ch-ua-mobile: ?1',
        '-H', 'sec-ch-ua-platform: "Android"',
        '-H', 'sec-fetch-dest: empty',
        '-H', 'sec-fetch-mode: cors',
        '-H', 'sec-fetch-site: same-origin',
        '-H', 'x-api-version: 3',
        '-H', 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ',
        '-d', f'{{"text":"{user_input}","conversation":"14KD7b4aR8HAxnpbFJB6s"}}'
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to get chat response: {e}")
        st.error(f"Curl stderr: {e.stderr}")
        return None

def execute_voice_curl(message_sid, voice="voice8"):
    curl_command = [
        'curl', '-X', 'GET', f'https://pi.ai/api/chat/voice?mode=eager&voice={voice}&messageSid={message_sid}',
        '-H', 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        '-H', 'authority: pi.ai',
        '-H', 'accept-language: en-PH,en-US;q=0.9,en;q=0.8',
        '-H', 'range: bytes=0-',
        '-H', 'referer: https://pi.ai/talk',
        '-H', 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"',
        '-H', 'sec-ch-ua-mobile: ?1',
        '-H', 'sec-ch-ua-platform: "Android"',
        '-H', 'sec-fetch-dest: audio',
        '-H', 'sec-fetch-mode: no-cors',
        '-H', 'sec-fetch-site: same-origin',
        '-H', 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ'
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, check=True)
        return io.BytesIO(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to get voice audio: {e}")
        st.error(f"Curl stderr: {e.stderr}")
        return None

def parse_chat_response(response):
    events = response.split('\n\n')
    message_sid = None
    response_text = ""
    
    for event in events:
        if event.startswith('event: message'):
            message_data = json.loads(event.split('\n', 2)[1].split(': ', 1)[1])
            message_sid = message_data['sid']
        elif event.startswith('event: partial'):
            partial_data = json.loads(event.split('\n', 2)[1].split(': ', 1)[1])
            response_text = partial_data['text']
    
    return response_text, message_sid

def main():
    st.title("PiVoice: Text-to-Speech with Pi AI")
    
    user_input = st.text_input("Enter your text:")
    voice_option = st.selectbox("Select voice:", ["voice1", "voice2", "voice3", "voice4", "voice5", "voice6", "voice7", "voice8"])
    
    if st.button("Generate Speech"):
        if user_input:
            with st.spinner("Processing..."):
                chat_response = execute_chat_curl(user_input)
                if chat_response:
                    response_text, message_sid = parse_chat_response(chat_response)
                    st.write(f"Pi AI response: {response_text}")
                    
                    if message_sid:
                        st.write("Generating audio...")
                        audio = execute_voice_curl(message_sid, voice_option)
                        if audio:
                            st.audio(audio, format="audio/mpeg")
                        else:
                            st.error("Failed to generate audio. Please try again.")
                    else:
                        st.error("Failed to get message ID. Please try again.")
                else:
                    st.error("Failed to get a response from Pi AI. Please try again later.")
        else:
            st.warning("Please enter some text.")

if __name__ == "__main__":
    main()
