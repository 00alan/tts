# this file contains functionality related to voice recognition and response

import os
import pyaudio
import wave
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import keyboard
from collections import deque

# local imports
from helpers import llm_helper as lh

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
    intro_text = "Hi, I'm your medical scheduling assistant and I'm here to help you. Use the spacebar when you are ready to ask me something."
    play_response(intro_text)

def listen_and_respond():
    # Set up the audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Press and hold the spacebar to speak; release to process. Press ESC to exit.")
    spacebar_pressed = False
    conversation_history = deque(maxlen=10)  # maintain context for llm

    frames = []  # A buffer to hold audio frames

    while True:
        if keyboard.is_pressed('space'):
            if not spacebar_pressed:
                spacebar_pressed = True
                frames = []  # Clear previous frames
                print("Listening...")
            data = stream.read(4096, exception_on_overflow=False)
            frames.append(data)
        elif spacebar_pressed:
            spacebar_pressed = False
            print("Processing...")
            # Write the frames to a temporary WAV file
            file_path = 'temp_audio.wav'
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))

            # Transcribe the audio file
            text = lh.transcribe_audio(file_path)
            if text:
                print("You said:", text)
                # Append the user's text to the history
                conversation_history.append({"role": "user", "content": text})

                # Assuming lh.get_llm_response is defined elsewhere and can handle the conversation history
                response_text = lh.get_llm_response(list(conversation_history))
                # Assuming play_response is defined elsewhere to play the response
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
