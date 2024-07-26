import streamlit as st
import requests
from sseclient import SSEClient
import io
import json

# Constants
CHAT_API_URL = "https://pi.ai/api/chat"
VOICE_API_URL = "https://pi.ai/api/chat/voice"
HEADERS = {
    'authority': 'pi.ai',
    'accept': 'text/event-stream',
    'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/json',
    'cookie': '__Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ',
    'origin': 'https://pi.ai',
    'referer': 'https://pi.ai/talk',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'x-api-version': '3'
}

VOICE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'authority': 'pi.ai',
    'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
    'range': 'bytes=0-',
    'referer': 'https://pi.ai/talk',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'audio',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-origin',
    'Cookie': '__Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ'
}

def get_chat_response(text):
    data = {
        "text": text,
        "conversation": "14KD7b4aR8HAxnpbFJB6s"
    }
    
    try:
        response = requests.post(CHAT_API_URL, headers=HEADERS, json=data, stream=True)
        response.raise_for_status()
        client = SSEClient(response)
        
        received_sid = None
        message_sid = None
        response_text = ""
        
        for event in client.events():
            if event.event == 'received':
                received_sid = json.loads(event.data)['sid']
            elif event.event == 'message':
                message_sid = json.loads(event.data)['sid']
            elif event.event == 'partial':
                response_text = json.loads(event.data)['text']
                break
        
        return response_text, received_sid, message_sid
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while communicating with the Pi AI chat API: {str(e)}")
        return None, None, None

def get_voice_audio(message_sid, voice="voice8"):
    url = f"{VOICE_API_URL}?mode=eager&voice={voice}&messageSid={message_sid}"
    
    try:
        response = requests.get(url, headers=VOICE_HEADERS)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to get voice audio: {str(e)}")
        return None

def main():
    st.title("PiVoice: Text-to-Speech with Pi AI")
    
    user_input = st.text_input("Enter your text:")
    voice_option = st.selectbox("Select voice:", ["voice1", "voice2", "voice3", "voice4", "voice5", "voice6", "voice7", "voice8"])
    
    if st.button("Generate Speech"):
        if user_input:
            with st.spinner("Processing..."):
                response_text, received_sid, message_sid = get_chat_response(user_input)
                if response_text:
                    st.write(f"Pi AI response: {response_text}")
                    
                    st.write("Generating audio...")
                    audio = get_voice_audio(message_sid, voice_option)
                    if audio:
                        st.audio(audio, format="audio/mp3")
                    else:
                        st.error("Failed to generate audio. Please try again.")
                else:
                    st.error("Failed to get a response from Pi AI. Please try again later.")
        else:
            st.warning("Please enter some text.")

if __name__ == "__main__":
    main()
