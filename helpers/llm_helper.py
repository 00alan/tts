# this file contains functionality related to llm prompting

from openai import OpenAI
from dotenv import load_dotenv
import os

# local imports
from helpers import calendar_helper as ch

# Automatically find and load environment variables from .env file
load_dotenv()
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def get_llm_response(context):
    """Send a user query to OpenAI and get a response."""
    try:
        messages=[
            {"role": "system", "content": "Decide what kind of response to generate.\
            If the user is providing details for an appointment (text must contain date and time) respond only\
            with the text '#VERIFY#'.\
            If is inquiring about an appointment, but without providing details, respond only with the text '#DETAILS#'.\
            If it is some other kind of scheduling, appointment, or availability related inquiry, respond only with the text '#SCHEDULING#'\
            If it is not scheduling/appointment/availability related, respond to the original inquiry as you naturally would."}]
        messages.extend(context),
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        response = completion.choices[0].message.content

        if "#SCHEDULING#" in response:
            # Get free/busy information
            busy_periods = ch.get_freebusy()
            # prompt gpt again with system content containing the busy periods
            messages=[{"role": "system", "content": f"Please respond to the user's inquiry, bearing in mind your knowledge that doctor is unavailable for the following periods: " + str(busy_periods) + f" - this information may, or may not, need to be mentioned in your helpful response to the user. Also bear in mind that today's date is {ch.get_today_date()}. Omit saying the year from any dates you mention."}]
            messages.extend(context),
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=150
            )
            response = completion.choices[0].message.content

        if '#DETAILS#' in response:
            messages=[{"role": "system", "content": "Prompt the user for the date, time, and their own name."}]
            messages.extend(context)
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=150
            )
            response = completion.choices[0].message.content

        if '#VERIFY#' in response:
            busy_periods = ch.get_freebusy()
            messages=[{"role": "system", "content": "Please verify that the appointment (assumed to be 59minutes length if not specified, so end time needs to be checked also) does not conflict with doctor John's schedule, bearing in mind that doctor John is unavailable for the following periods: " + str(busy_periods) + f". Also bear in mind that today's date is {ch.get_today_date()}. If the appointment conflicts, describe the scheduling conflict to the user. If the appointment does not conflict, and the user has already provided their name, only respond with '#CONFIRMED#:' followed by the appointment details. If they have not yet provided their name, you must prompt them for it."}]
            messages.extend(context)
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=150
            )
            response = completion.choices[0].message.content

            if '#CONFIRMED#:' in response:
                completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"Unless otherwise specified, assume that the appointment is being scheduled in the current year (today's date is {ch.get_today_date()}). Please return a string containing the appointment start time into ISO format, followed by a space, followed by the name they provided."},
                        {"role": "user", "content": response}
                    ],
                    max_tokens=150
                )
                response = completion.choices[0].message.content
                start_time_iso, name = response.split(' ', 1)
                ch.create_event(start_time_iso, name)
                # extract date and time from start_time_iso
                date = start_time_iso[:10]
                time = start_time_iso[11:16]
                response = f"Appointment with {name} scheduled for {date} at {time}."

        return response

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm sorry, I couldn't process your request."
