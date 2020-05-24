from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient import discovery
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import timedelta

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def main():
    """
    Пусто
    """


def check_time(start_time, end_time):
    """
    Принимает дату от пользователя, и проверяет, занято ли это время
    :param end_time: конец процедуры
    :param start_time: начало процедуры
    :param date: дата в формате  2020-01-20T09:00:00Z
    :return: True - время свободно, False - занято
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    start_time = start_time - timedelta(hours=3)
    start_time = start_time.isoformat() + "Z"
    end_time = end_time - timedelta(hours=3)
    end_time = end_time.isoformat() + "Z"
    events_result = service.events().list(calendarId='primary', timeMin=start_time,
                                          timeMax=end_time).execute()
    events = events_result.get('items', [])

    if not events:
#        print("confirmation")
        return "confirmation"
    for event in events:
        starttime = event['start'].get('dateTime', event['start'].get('date'))
        endtime = event['end'].get('dateTime', event['end'].get('date'))
#        print("К сожалению, Оксана ЗАНЯТА", "с", starttime[11:16], "до", endtime[11:16])
        return "time"


def check_date(date):
    """
    Принимает на вход дату от пользователя, и выводит все события в этот день
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
#    date += "T00:00:00"
#    date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    date = date.isoformat() + "Z"
#    print('На этот день у Оксаны следующие записи:')
    events_result = service.events().list(calendarId='primary', timeMin=date[:11] + "00" + date[-7:],
                                          timeMax=date[:11] + "23:59:59Z",
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
#        print('Ближайших записей не найдено')
        return "записей пока нет"
    response = ""
    text = ""
    for event in events:
        starttime = event['start'].get('dateTime', event['start'].get('date'))
        endtime = event['end'].get('dateTime', event['end'].get('date'))
        response = (" с", starttime[11:16], "до", endtime[11:16])
        text += str(response)
    response = ("уже ЗАНЯТО время "
                + text.replace(")(", " и ").replace("(", "").replace("'", "").replace(",", "").replace(")", ""))
    return response
#        return str(text).replace("(", "").replace("'", "").replace(",", "").replace(")", "")
# Тут у нас кортеж, нужно преобразовать в строку


def create_event(name_of_subscriber, procedure, start_time, end_time):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API

    start_time = start_time - timedelta(hours=3)
    end_time = end_time - timedelta(hours=3)
    start_time = start_time.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_time = end_time.isoformat() + 'Z'  # 'Z' indicates UTC time
    event = {
        'summary': name_of_subscriber,
        'location': 'ул. Софьи Ковалевской, 16к5, кв. 262',
        'description': str(procedure),
        'start': {
            'dateTime': start_time,  # date format: '2020-01-20T09:00:00Z'
            'timeZone': 'Europe/Moscow',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Moscow',
        },
        'attendees': [
            {'email': 'kuwerin@gmail.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='6n1kf0r4h9cfdku2kvobiqaemc@group.calendar.google.com',
                                    body=event).execute()
#    print('Event created: %s' % (event.get('htmlLink')))


#text = "2020-03-12"  # С 18 часов - не работает. Протестить, что там с листом событий - не пишутся ли события с другого дня

#start = "2020-03-12T09:00:00"
#end = "2020-03-12T15:00:00"
#start1 = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
#end1 = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
#check_time(start1, end1)
#date1 = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
# check_time(date1)
# print(date1[:11] + "00" + date1[-7:])
# print(date1[:11] + "23:59:59Z")
# check_date(date1)

#check_date(text)
