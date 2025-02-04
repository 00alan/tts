# this file contains functionality related to voice recognition and response

from vosk import Model, KaldiRecognizer
import os
import pyaudio  # Library to handle live audio
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import keyboard
from collections import deque

# local imports
from helpers import llm_helper as lh

model_path = r"C:\Users\alane\Documents\GitHub\tts\vosk-model-small-en-us-0.15"
#model_path = r"C:\Users\alane\Documents\GitHub\tts\vosk-model-en-us-0.22-lgraph"
#model_path = r"C:\Users\alane\Documents\GitHub\tts\vosk-model-en-us-0.42-gigaspeech"

def play_response(text):
    filename = "response.mp3"
    # Remove asterisks from the text
    text = text.replace('*', '')
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
    conversation_history = deque(maxlen=10) # maintain context for llm
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
                # Append the user's text to the history
                conversation_history.append({"role": "user", "content": text})

                # Get response from the LLM
                response_text = lh.get_llm_response(list(conversation_history))
                play_response(response_text)

                # Print and append the assistant's response to the history
                print("\nAssistant response:", response_text, '\n')
                conversation_history.append({"role": "assistant", "content": response_text})
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()
