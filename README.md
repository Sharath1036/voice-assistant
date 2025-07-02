# Voice Assistant

## Setup
Tech Stack: `Python 3.11.0`

Clone the code
```
git clone https://github.com/Sharath1036/voice-assistant.git
```

Create a virtual enviornment
```
python -m venv myenv
```
Activate the venv
```
myenv\Scripts\activate
```
Install the dependencies
```
pip install -r requirements.txt
```
Create a `.env` file and add your Groq API Key and OpenAI API KEY
```
GROQ_API_KEY = '...'
OPENAI_API_KEY = '...'
```
`GROQ_API_KEY` is used for transcribing the sentence using `whisper-large-v3` model and generating the response using `llama-3.3-70b-versatile` model. 
`OPENAI_API_KEY` is used for performing web search when we ask the assistant about the latest news.

Run the code
```
python main.py
```

To exit the voice assistant say `exit`, `quit` or `stop` while the assistant is listening.