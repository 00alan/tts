import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

from helpers import calendar_helper as ch

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Define the scopes (ensure to use the scope that allows writing)
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Create credentials from the service account key file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the service object for the Calendar API using the credentials
service = build('calendar', 'v3', credentials=credentials)

# Calculate the date and time for the new event
tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
start_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 3, 0)  # 3 AM UTC
end_time = start_time + datetime.timedelta(hours=1)  # 1 hour long meeting
print(start_time.isoformat())
print(end_time.isoformat())

# Create event details
event = {
    'summary': 'New Meeting',
    'location': 'Virtual',
    'description': 'Discussing important topics.',
    'start': {
        'dateTime': start_time.isoformat(),
        'timeZone': 'UTC',
    },
    'end': {
        'dateTime': end_time.isoformat(),
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

# Call the Calendar API to add the event
calendar_id =  '00alan.edmonds@gmail.com'
event_result = service.events().insert(calendarId=calendar_id, body=event).execute()

# Print the event details
print(f"Event created: {event_result.get('htmlLink')}")

# create a meeting on feb 6 at 6am
ch.create_event('2025-02-06T06:00:00', 'Dr Joe')
