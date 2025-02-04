from vosk import Model, KaldiRecognizer
import os
import pyaudio  # Library to handle live audio
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import keyboard
from openai import OpenAI
from dotenv import load_dotenv
import requests

# Automatically find and load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key=os.getenv('openai_api_key')
)

model_path = r"C:\Users\alane\Documents\GitHub\tts\vosk-model-small-en-us-0.15"
#model_path = r"C:\Users\alane\Documents\GitHub\tts\vosk-model-en-us-0.42-gigaspeech"

def get_llm_response(text):
    """Send a user query to OpenAI and get a response with scheduling decision."""
    try:
        # Send the user's question to GPT to decide if it's a scheduling question
        decision_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            max_tokens=150,
            user="Decide if the following is a scheduling question and respond accordingly."
        )

        decision_content = decision_completion.choices[0].message.content.strip()

        # If it is a scheduling question, construct a Google Calendar API request
        if "scheduling" in decision_content.lower():
            # Construct the Google Calendar API request
            calendar_response = requests.get("YOUR_CALENDAR_API_ENDPOINT", params={"query": text})

            if calendar_response.status_code == 200:
                # Append calendar info to the original question
                calendar_info = calendar_response.json()  # Assume JSON response
                full_question = f"{text} With the following calendar info: {calendar_info}"

                # Send the modified question back to GPT
                answer_completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": full_question}],
                    max_tokens=150
                )
                return answer_completion.choices[0].message.content
            else:
                return "Failed to retrieve calendar information."

        # If not a scheduling question, answer as usual
        else:
            return decision_content

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm sorry, I couldn't process your request."

def play_response(text):
    filename = "response.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        audio = AudioSegment.from_mp3(filename)
        play(audio)
    except Exception as e:
        print("Error playing back response:", str(e))
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def play_intro():
    intro_text = "Hi, I'm your bot and I'm here to help you. Hold the spacebar when you are ready to ask me something."
    play_response(intro_text)

def listen_and_respond():    
    if not os.path.exists(model_path):
        print(f"Model path {model_path} does not exist, please check the location and try again.")
        return
    
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    # Set up the audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Press and hold the spacebar to speak; release to process. Press ESC to exit.")
    spacebar_pressed = False
    while True:
        if keyboard.is_pressed('space'):
            if not spacebar_pressed:
                spacebar_pressed = True
                print("Listening...")
            data = stream.read(4096, exception_on_overflow=False)
            recognizer.AcceptWaveform(data)
        elif spacebar_pressed:
            spacebar_pressed = False
            result = json.loads(recognizer.Result())
            text = result.get('text', '')
            if text:
                print("Processing your question:", text)
                response_text = get_llm_response(text)
                play_response(response_text)
                print("\nAssistant reponse:", response_text, '\n')
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break


    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    play_intro()
    listen_and_respond()
