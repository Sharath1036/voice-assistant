from groq import Groq
import openai
import pyttsx3
import speech_recognition as sr
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from os import getenv
from dotenv import load_dotenv

class VoiceAssistant:
    def __init__(self, creds_path, sheet_name):
        load_dotenv(override=True)
        
        self.client = Groq(api_key=getenv("GROQ_API_KEY"))
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.sheet = self.init_google_sheet(creds_path, sheet_name)
        self.recognizer.pause_threshold = 1.0  # Default is 0.8 seconds; try 1.0 or higher

    def init_google_sheet(self, creds_path, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        return client.open(sheet_name).sheet1

    def listen(self):
        with sr.Microphone() as source:
            print("🎙️ Listening...")
            audio = self.recognizer.listen(source)
            with open("temp.wav", "wb") as f:
                f.write(audio.get_wav_data())
        return "temp.wav"

    def transcribe(self, audio_path):
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        print(f"🗣️ User: {transcript}")
        return transcript

    def query_llama(self, prompt):
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        print(f"🤖 LLaMA: {reply}")
        return reply

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def log(self, user_input, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Logging to sheet: {timestamp}, {user_input}, {response}")
        try:
            self.sheet.append_row([timestamp, user_input, response])
            print("Logged successfully.")
        except Exception as e:
            print(f"Failed to log to Google Sheet: {e}")

    def run(self):
        print("Say 'exit' or 'quit' to end the conversation.")
        while True:
            audio_file = self.listen()
            user_input = self.transcribe(audio_file)
            if user_input.strip().lower() in ["exit", "quit", "stop"]:
                print("👋 Goodbye!")
                self.speak("Goodbye!")
                break
            response = self.query_llama(user_input)
            self.speak(response)
            self.log(user_input, response)

if __name__ == "__main__":
    bot = VoiceAssistant(
        creds_path="google_creds.json",
        sheet_name="voice-ai-logging"
    )
    bot.run()
