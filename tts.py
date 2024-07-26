import streamlit as st
import subprocess
import json
import time
import os
import requests
import re
import base64
from io import BytesIO

CONVERSATIONS_CURL = '''
curl -X POST 'https://pi.ai/api/conversations' -H 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36' -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'authority: pi.ai' -H 'accept-language: en-PH,en-US;q=0.9,en;q=0.8' -H 'origin: https://pi.ai' -H 'referer: https://pi.ai/talk' -H 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"' -H 'sec-ch-ua-mobile: ?1' -H 'sec-ch-ua-platform: "Android"' -H 'sec-fetch-dest: empty' -H 'sec-fetch-mode: cors' -H 'sec-fetch-site: same-origin' -H 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=28MnnefdTV23iLTtJaYJdxU6magLYb4zpDGyMKHrHvw-1721964119-1.0.1.1-upkx6n8USULq_B4mAxmjY2Y1fh40DkcftOZXoRwQTHh0Th4MtCGN0Jin02G7ALcqrnx3huEnpGbujKoW9ETsBw' -d '{}'
'''

CHAT_CURL = '''
curl -X POST 'https://pi.ai/api/chat' -H 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36' -H 'Accept: text/event-stream' -H 'Content-Type: application/json' -H 'authority: pi.ai' -H 'accept-language: en-PH,en-US;q=0.9,en;q=0.8' -H 'origin: https://pi.ai' -H 'referer: https://pi.ai/talk' -H 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"' -H 'sec-ch-ua-mobile: ?1' -H 'sec-ch-ua-platform: "Android"' -H 'sec-fetch-dest: empty' -H 'sec-fetch-mode: cors' -H 'sec-fetch-site: same-origin' -H 'x-api-version: 3' -H 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ' -d '{}'
'''

VOICE_CURL = '''
curl -X GET 'https://pi.ai/api/chat/voice?mode=eager&voice=voice6&messageSid={}' -H 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36' -H 'authority: pi.ai' -H 'accept-language: en-PH,en-US;q=0.9,en;q=0.8' -H 'range: bytes=0-' -H 'referer: https://pi.ai/talk' -H 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"' -H 'sec-ch-ua-mobile: ?1' -H 'sec-ch-ua-platform: "Android"' -H 'sec-fetch-dest: audio' -H 'sec-fetch-mode: no-cors' -H 'sec-fetch-site: same-origin' -H 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ'
'''

class ChatTTSApp:
    def __init__(self):
        self.conversation_id = self.get_conversation_id()
        self.bad_words = self.load_bad_words()
        self.bad_word_patterns = self.compile_bad_word_patterns()

    def run_curl(self, curl_command):
        try:
            result = subprocess.run(curl_command, shell=True, check=True, capture_output=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            st.error(f"Error running curl command: {e}")
            st.error(f"Stderr: {e.stderr}")
            return None

    def get_conversation_id(self):
        response = self.run_curl(CONVERSATIONS_CURL)
        try:
            data = json.loads(response)
            return data.get('sid')
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON: {response}")
            return None

    def load_bad_words(self):
        url = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en"
        response = requests.get(url)
        if response.status_code == 200:
            return set(response.text.split())
        else:
            st.warning("Failed to load bad words list. Continuing without word filtering.")
            return set()

    def compile_bad_word_patterns(self):
        return [re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE) for word in self.bad_words]

    def contains_bad_word(self, message):
        return any(pattern.search(message) for pattern in self.bad_word_patterns)

    def send_message(self, message):
        if self.contains_bad_word(message):
            return "Blocked", None

        chat_data = json.dumps({"text": message, "conversation": self.conversation_id})
        chat_curl = CHAT_CURL.replace("'{}'", f"'{chat_data}'")
        response = self.run_curl(chat_curl)

        if response is None:
            return None, None

        received_sid = None
        full_response = ""
        for line in response.decode('utf-8').splitlines():
            if line.startswith('event: received'):
                received_data = json.loads(next(line for line in response.decode('utf-8').splitlines() if line.startswith('data:')).split('data: ')[1])
                received_sid = received_data.get('sid')
            elif line.startswith('data:'):
                try:
                    event_data = json.loads(line[5:])
                    if 'text' in event_data:
                        full_response += event_data['text']
                except json.JSONDecodeError:
                    st.error(f"Error decoding JSON: {line}")

        return full_response.strip(), received_sid

    def get_voice(self, message_sid):
        voice_curl = VOICE_CURL.format(message_sid)
        voice_response = self.run_curl(voice_curl)
        
        if voice_response is None:
            return None

        return voice_response

def main():
    st.set_page_config(page_title="ChatTTS App", page_icon="🗣️")
    st.title("ChatTTS App")

    if 'chat_app' not in st.session_state:
        st.session_state.chat_app = ChatTTSApp()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is your message?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response, received_sid = st.session_state.chat_app.send_message(prompt)
            if response == "Blocked":
                st.error("Your message was blocked due to inappropriate content.")
            elif response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                if received_sid:
                    voice_data = st.session_state.chat_app.get_voice(received_sid)
                    if voice_data:
                        st.audio(voice_data, format="audio/mp3")
                    else:
                        st.error("Failed to get voice response.")
                else:
                    st.warning("No 'received' event SID found in the response.")
            else:
                st.error("Failed to get a response. Please try again.")

if __name__ == "__main__":
    main()
