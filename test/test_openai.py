from openai import OpenAI
from dotenv import load_dotenv
import os

# Automatically find and load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "hello there"}
  ]
)

print(completion.choices[0].message.content)
print()
print()
print(completion)
