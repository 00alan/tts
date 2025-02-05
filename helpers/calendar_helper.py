# this file contains functionality related to Google Calendar API

from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Create credentials from the service account key file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the service object for the Calendar API using the credentials
service = build('calendar', 'v3', credentials=credentials)

def compactify_periods(busy_periods):
    """Function to group and compactify response from free/busy query by date."""
    # Outputs a dictionary where each date has a list of tuples representing start and end times.
    compact_periods = {}
    for period in busy_periods:
        date = period['start'][:10]  # Extract the date 'YYYY-MM-DD'
        start_time = period['start'][11:16]  # Extract and format the start time 'HH:MM'
        end_time = period['end'][11:16]  # Extract and format the end time 'HH:MM'
        
        # Append the start and end time tuple to the list of times for the corresponding date
        if date not in compact_periods:
            compact_periods[date] = []
        compact_periods[date].append((start_time, end_time))
    
    return compact_periods

def get_freebusy(days=60):
    # Define the time range for free/busy query
    time_min = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    time_max = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + 'Z'

    # Construct the freeBusy query
    calendar_id =  '00alan.edmonds@gmail.com'
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": calendar_id}]
    }

    # Call the freeBusy API
    response = service.freebusy().query(body=body).execute()
    busy_periods = response['calendars'][calendar_id]['busy']
    return compactify_periods(busy_periods)

def create_event(start_time_iso, name):  # start_time_iso will be in ISO format
    # Parse the ISO formatted time into a datetime object for time manipulation
    start_time = datetime.datetime.fromisoformat(start_time_iso)
    event = {
        'summary': 'Appointment',
        'location': 'Virtual',
        'description': 'Appointment with ' + name,
        'start': {
            'dateTime': start_time_iso,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (start_time + datetime.timedelta(hours=1)).isoformat(), # 1 hour long meeting default
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    calendar_id =  '00alan.edmonds@gmail.com'
    event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: %s' % (event_result.get('htmlLink')))

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")
    