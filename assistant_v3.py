import speech_recognition as sr
import openai
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import keyboard

# Set your OpenAI API key here
openai.api_key = 'your-openai-api-key'

def get_llm_response(text):
    # Placeholder for sending a prompt to the GPT model and getting a response
    return "Sorry, I am unable to help at this time."

def play_response(text):
    # Using gTTS to convert text to speech
    filename = "response.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        # Using pydub to play the response
        audio = AudioSegment.from_mp3(filename)
        play(audio)
    except Exception as e:
        print("Error playing back response:", str(e))
    finally:
        if os.path.exists(filename):
            os.remove(filename)  # Remove the file after playing it

def play_intro():
    intro_text = "Hi, I'm your bot and I'm here to help you. Hold the spacebar when you are ready to ask me something."
    play_response(intro_text)

def listen_and_respond():
    recognizer = sr.Recognizer()
    print("Press and hold the spacebar to speak; release to process. Press ESC to exit.")
    while True:
        if keyboard.is_pressed('space'):  # Start recording when space is pressed
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
                print("Listening... Release the spacebar when finished speaking.")
                audio = recognizer.listen(source)
            try:
                # Directly use the audio data for recognition
                text = recognizer.recognize_google(audio, language="en-US")
                print("Processing your question: " + text)
                response_text = get_llm_response(text)
                print("Assistant is responding...")
                play_response(response_text)
            except sr.UnknownValueError:
                print("Could not understand audio. Please try again.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                print(str(e))
        if keyboard.is_pressed('esc'):  # Exit on ESC
            print("Exiting...")
            break

if __name__ == "__main__":
    play_intro()
    listen_and_respond()
