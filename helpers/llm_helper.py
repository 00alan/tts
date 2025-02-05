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

def get_llm_response(context):
    """Send a user query to OpenAI and get a response."""
    try:
        messages=[
            {"role": "system", "content": "Decide if the user has a scheduling or appointment related inquiry.\
            If it is not scheduling related, respond to the original inquiry naturally.\
            If the user is providing details for an appointment (text must contain date and time) respond only\
            with the text 'VERIFY'.\
            If is inquiring about an appointment, but without providing details, respond only with the text 'DETAILS'.\
            Otherwise, respond only with the text 'SCHEDULING'"}]
        messages.extend(context),
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150
        )
        response = completion.choices[0].message.content

        if response == "SCHEDULING":
            # Get free/busy information
            busy_periods = ch.get_freebusy()
            # prompt gpt again with system content containing the busy periods
            messages=[{"role": "system", "content": f"Please respond to the user's inquiry, bearing in mind your knowledge that doctor Joe is unavailable for the following periods: " + str(busy_periods) + f" - this information may, or may not, need to be mentioned in your helpful response to the user. Also bear in mind that today's date is {ch.get_today_date()}. Omit saying the year from any dates you mention."}]
            messages.extend(context),
            completion = client.chat.completions.create(
                #model="o3-mini", # more complex reasoning model for secondary prompt 
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150
            )
            response = completion.choices[0].message.content

        if response == "DETAILS":
            messages=[{"role": "system", "content": "Prompt the user for the date, time, and their own name."}]
            messages.extend(context)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150
            )
            response = completion.choices[0].message.content

        if response == "VERIFY":
            busy_periods = ch.get_freebusy()
            messages=[{"role": "system", "content": "Please verify that the appointment (assumed to be 1hr length if not specified) does not conflict with doctor Joe's schedule, bearing in mind that doctor Joe is unavailable for the following periods: " + str(busy_periods) + ". If the appointment conflicts, describe the scheduling conflict to the user. If the appointment does not conflict, and the user has already provided their name, only respond with 'CONFIRMED:' followed by the appointment details. If they have not provided their name, prompt them for it."}]
            messages.extend(context)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
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
