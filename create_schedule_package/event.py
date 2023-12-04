

# built-in python imports
from dataclasses import dataclass
import datetime

# local imports
from exceptions import *
import get_calendar_data


@dataclass
class Event:

    topic: str
    duration: int
    study_type: str

    # def __init__(self, topic, duration, study_type):
    #     self.topic = topic
    #     self.duration = duration
    #     self.study_type = study_type
    #     self.start_time = self.end_time = "pending"

    def set_start_and_end_times(self, start_and_end_times: dict):
        self.start_time = start_and_end_times['start']
        self.end_time = start_and_end_times['end']

    def __str__(self):
        return f"Topic: {self.topic}, Duration: {self.duration}, Study Type: {self.study_type}"

    def create_google_calendar_event(self):

        def convert_times_to_google_format():
            '''
            converts event.start_time and event.end_time from dateTime object of format (2023-11-20 T09:00:00-08:00)
            into a string of format (2023-11-20 T09:00:00) which is the format used to create a google calendar event
            '''
            def add_T_to_time_string(time_string: str):
                date = time_string.split(' ')[0]
                time = time_string.split(' ')[1]
                time_string = date + 'T' + time
                
                return time_string
            
            google_format_start_time = str(self.start_time)[:-6]
            google_format_end_time = str(self.end_time)[:-6]

            google_format_start_time = add_T_to_time_string(google_format_start_time)
            google_format_end_time = add_T_to_time_string(google_format_end_time) 

            self.start_time = google_format_start_time
            self.end_time = google_format_end_time

        def add_event_to_google_calendar(event: Event):
            service = get_calendar_data.access_calendar()
            event = service.events().insert(calendarId='primary', body=event).execute()


        convert_times_to_google_format()

        google_event = {
            'summary': self.topic + ' - ' + self.study_type,
            'description': 'NA',
            'start': {'dateTime': self.start_time, 'timeZone': "America/Los_Angeles"},
            'end': {'dateTime': self.end_time, 'timeZone': "America/Los_Angeles"},
            'reminders': {
                'useDefault': False,
                'overrides': [],
            },
        }

        add_event_to_google_calendar(google_event)


    # --- Data Validation ---
    # TODO: this function is not implemented in code yet
    def data_validation(self):
        # NOTE: try-except-except blocks are use when you DONT want the program to crash. 
        # In this case, I want to just raise exception
        
        time_difference = (self.end_time - self.start_time).total_seconds() / 60
        if time_difference != self.duration:
            raise StartEndDurationMismatchError


class MemoryBlockEvent(Event):
    
    def __init__(self, topic, duration, study_type, study_duration, recall_duration):
        super().__init__(topic, duration, study_type)
        self.study_type = 'memory block'
        self.study_event = Event(self.topic, study_duration, 'study')
        self.recall_event = Event(self.topic, recall_duration, 'recall')       


    def set_start_and_end_times(self, start_and_end_times: dict):
        super().set_start_and_end_times(start_and_end_times)
        self.study_event.start_time = self.start_time
        self.study_event.end_time = self.study_event.start_time + datetime.timedelta(minutes = self.study_event.duration)
        
        self.recall_event.start_time = self.study_event.end_time
        self.recall_event.end_time = self.end_time


    def __str__(self):
        return f"MemoryBlockEvent: \n\tTopic: {self.topic}, Duration: {self.duration} \n\tStudy Event: ({self.study_event}) \n\tRecall Event: ({self.recall_event})"
        
    def create_google_calendar_event(self):
        self.study_event.create_google_calendar_event()
        self.recall_event.create_google_calendar_event()
