from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

from settings import CALENDER_ID

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar'
]


class GoogleCalnderHandler:
    def __init__(self) -> None:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_events(self, year: Optional[int] = None, month: Optional[int] = None, day: Optional[int] = None, calender_id: Optional[str] = CALENDER_ID, max_result_num: int = 100) -> List[Dict[str, Any]]:
        now = datetime.now()
        now_time_text = datetime(
            year=year if year is not None else now.year,
            month=month if month is not None else now.month,
            day=day if day is not None else 1
        ).isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId=calender_id,
            timeMin=now_time_text,
            maxResults=max_result_num,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])

    def add_event(self,
                  title: str,
                  start_datetime: datetime,
                  end_datetime: datetime,
                  location: Optional[str],
                  ) -> Dict[str, Any]:
        event_param = {
            'summary': title,
            'location': location,
            'start': {
                'dateTime': start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Japan',
            },
        }
        event: Dict[str, Any] = self.service.events().insert(
            calendarId=CALENDER_ID,
            body=event_param
        ).execute()

        return event

    def delete_event(self, event_id: str) -> None:
        res = self.service.events().delete(
            calendarId=CALENDER_ID,
            eventId=event_id
        ).execute()

    @classmethod
    def time_text_to_datetime(cls, time_text: str) -> datetime:
        return datetime.strptime(time_text[:-6], "%Y-%m-%dT%H:%M:%S")


if __name__ == '__main__':
    handler = GoogleCalnderHandler()
    from pprint import pprint

    events = handler.get_events()

    for event in events:
        handler.delete_event(event['id'])
