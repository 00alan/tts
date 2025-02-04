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

# Define the time range for free/busy query
days = 60
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
print(response)
busy_periods = response['calendars'][calendar_id]['busy']

def compactify_periods(busy_periods):
    # Function to group and compactify periods by date.
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

print()
print(compactify_periods(busy_periods))
