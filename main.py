'''
Link to the spreadsheet: https://docs.google.com/spreadsheets/d/1Q_hYZ9kGC3Ab1kGmnY-QJXeVMLzdWNi_TDTJEuhvBS0/edit?gid=0#gid=0 
Link to the project: https://github.com/Sharath1036/voice-assistant
'''

from groq import Groq
import openai
import pyttsx3
import speech_recognition as sr
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.groq import Groq as GroqModel
import re

class VoiceAssistant:
    def __init__(self, creds_path, sheet_name):
        load_dotenv(override=True)
        
        self.client = Groq(api_key=getenv("GROQ_API_KEY"))
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.sheet = self.init_google_sheet(creds_path, sheet_name)
        self.recognizer.pause_threshold = 1.0
        
        # Initialize web search agent
        self.search_agent = Agent(
            tools=[DuckDuckGoTools()], 
            show_tool_calls=True,
            markdown=True
        )

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

    def needs_web_search(self, prompt):
        """Determine if the query needs web search"""
        search_keywords = [
            "search", "find", "what's happening", "latest", "news", 
            "current", "today", "recent", "weather", "stock", 
            "price", "update", "information about", "who won", "who is", "who was", "who are", "who did"
        ]
        # Check for keywords
        if any(keyword in prompt.lower() for keyword in search_keywords):
            print("[DEBUG] Web search triggered by keyword.")
            return True
        # Check for years in the range 2020-2035 (adjust as needed)
        year_match = re.search(r"\b20[2-3][0-9]\b", prompt)
        if year_match:
            print(f"[DEBUG] Web search triggered by year: {year_match.group(0)}")
            return True
        # Check for question words
        if re.match(r"^(who|what|when|where|why|how)\b", prompt.lower()):
            print("[DEBUG] Web search triggered by question word.")
            return True
        print("[DEBUG] No web search triggered.")
        return False

    def web_search(self, query):
        """Perform web search using DuckDuckGo"""
        try:
            # Use the search agent to get web results
            response = self.search_agent.run(query)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"Web search error: {e}")
            return f"I couldn't search the web right now. Error: {str(e)}"

    def query_llama(self, prompt):
        print(f"[DEBUG] Checking if web search is needed for prompt: {prompt}")
        if self.needs_web_search(prompt):
            print("🔍 Performing web search...")
            search_result = self.web_search(prompt)
            print(f"[DEBUG] Web search result: {search_result}")

            enhanced_prompt = f"""
            Based on the following web search results, please provide a comprehensive answer:

            Web Search Results:
            {search_result}

            Original Question: {prompt}

            Please provide a clear, concise answer based on the search results above.
            """
            print(f"[DEBUG] Enhanced prompt: {enhanced_prompt}")

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": enhanced_prompt}]
            )
        else:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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
        print("You can now ask for web searches! Try: 'What's happening in France?' or 'Search for latest AI news'")
        while True:
            audio_file = self.listen()
            user_input = self.transcribe(audio_file)
            user_input_str = str(user_input)
            if user_input_str.strip().lower() in ["exit", "quit", "stop"]:
                print("👋 Goodbye!")
                self.speak("Goodbye!")
                break
            response = self.query_llama(user_input_str)
            self.speak(response)
            self.log(user_input_str, response)

if __name__ == "__main__":
    bot = VoiceAssistant(
        creds_path="google_creds.json",
        sheet_name="voice-ai-logging"
    )
    bot.run()