# Voice Assistant

## Setup
Tech Stack: `Python 3.11.0`

Clone the code
```
git clone https://www.github.com/Sharath1036/voice-assistant
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
Create a `.env` file and add your Groq API Key
```
GROQ_API_KEY = '...'
```
Run the code
```
python main.py
```

To exit the voice assistant say `exit`, `quit` or `stop` while the assistant is listening.