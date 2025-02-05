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
                {"role": "system", "content": "Decide if the user has a scheduling or appointment related inquiry.\
                    If it is not scheduling related, respond to the original inquiry naturally.\
                    If the user is providing details for an appointment (text must contain all three of date, time, and name) respond only with the text 'VERIFY'.\
                    If it is a direct request to make an appointment, but without details provided, respond only with the text 'DETAILS'.\
                    Otherwise, respond only with the text 'SCHEDULING'"},
                {"role": "user", "content": text}
            ],
            max_tokens=150
        )
        response = completion.choices[0].message.content

        if response == "SCHEDULING":
            # Get free/busy information
            busy_periods = ch.get_freebusy()
            # prompt gpt again with system content containing the busy periods
            completion = client.chat.completions.create(
                #model="o3-mini", # more complex reasoning model for secondary prompt 
                model="gpt-4o-mini",
                messages=[
                    #{"role": "system", "content": f"Please respond to the user's inquiry, bearing in mind your knowledge that doctor Joe is unavailable for the following periods: " + str(busy_periods) + f" - this information may, or may not, need to be mentioned in your helpful response to the user. Also bear in mind that today's date is {ch.get_today_date()}. If the user's inquiry would require knowledge of the doctor's schedule beyond the next {days} days, please let the user know that you do not have that information."},
                    {"role": "system", "content": f"Please respond to the user's inquiry, bearing in mind your knowledge that doctor Joe is unavailable for the following periods: " + str(busy_periods) + f" - this information may, or may not, need to be mentioned in your helpful response to the user. Also bear in mind that today's date is {ch.get_today_date()}. Omit saying the year from any dates you mention."},
                    {"role": "user", "content": text}
                ],
                max_tokens=150
            )
            response = completion.choices[0].message.content

        if response == "DETAILS":
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Prompt the user for the date, time, and their own name."},
                    {"role": "user", "content": text}
                ],
                max_tokens=150
            )
            response = completion.choices[0].message.content

        if response == "VERIFY":
            busy_periods = ch.get_freebusy()
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Please verify that the appointment (assumed to be 1hr length if not specified) does not conflict with doctor Joe's schedule, bearing in mind that doctor Joe is unavailable for the following periods: " + str(busy_periods) + ". If the appointment conflicts, describe the scheduling conflict to the user. If the appointment does not conflict, only respond with 'CONFIRMED:' followed by the appointment details."},
                    {"role": "user", "content": text}
                ],
                max_tokens=150
            )
            response = completion.choices[0].message.content

            if response[:9] == "CONFIRMED":
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Please return a string containing the appointment start time into ISO format, followed by a space, followed by the name of the person the appointment is with."},
                        {"role": "user", "content": response}
                    ],
                    max_tokens=150
                )
                response = completion.choices[0].message.content
                print(response)
                start_time_iso, name = response.split(' ')
                ch.create_event(start_time_iso, name)
                # extract date and time from start_time_iso
                date = start_time_iso[:10]
                time = start_time_iso[11:16]
                response = f"Appointment with {name} scheduled for {date} at {time}."

        return response

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm sorry, I couldn't process your request."
