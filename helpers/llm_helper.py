# this file contains functionality related to llm prompting

from openai import OpenAI
from dotenv import load_dotenv
import os

# Automatically find and load environment variables from .env file
load_dotenv()
client = OpenAI(
    api_key=os.getenv('openai_api_key')
)

def get_llm_response(text):
    """Send a user query to OpenAI and get a response."""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": text}],
            max_tokens=150
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm sorry, I couldn't process your request."
