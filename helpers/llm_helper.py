# this file contains functionality related to llm prompting

from openai import OpenAI
from dotenv import load_dotenv
import os

# local imports
from helpers import calendar_helper as ch

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
            messages=[
                {"role": "system", "content": "Decide if the user has a scheduling or appointment related inquiry. \
                    If it is not scheduling related, respond to the original inquiry naturally. If it is, respond only with the text 'SCHEDULING'"},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        response = completion.choices[0].message.content

        if response == "SCHEDULING":
            # Get free/busy information
            days = 60
            busy_periods = ch.get_freebusy(days)
            # prompt gpt again with system content containing the busy periods
            completion = client.chat.completions.create(
                #model="o3-mini", # more complex reasoning model for secondary prompt 
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Please respond to the user's inquiry, applying your knowledge doctor John's busy periods \ for the next {days} days: " + str(busy_periods) + f" - this information may or may not be helpful in constructing a helpful response to the user. If the user's inquiry would require knowledge of the doctor's schedule beyond the next {days} days, please let the user know that you do not have that information."},
                    {"role": "user", "content": text}
                ],
                max_tokens=150
            )
            response = completion.choices[0].message.content

        return response

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm sorry, I couldn't process your request."
