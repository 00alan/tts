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
time_min = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
time_max = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + 'Z'

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
