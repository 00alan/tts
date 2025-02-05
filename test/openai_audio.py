import base64
import requests
from openai import OpenAI

from dotenv import load_dotenv
import os

# Automatically find and load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

"""
# Fetch the audio file and convert it to a base64 encoded string
url = "https://cdn.openai.com/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content
encoded_string = base64.b64encode(wav_data).decode('utf-8')
"""

# local audio file
filepath = '../temp_audio.wav'
with open(filepath, 'rb') as file:
    wav_data = file.read()
encoded_string = base64.b64encode(wav_data).decode('utf-8')


audio_file = open('../temp_audio.wav', "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="text"
)

print(transcription)