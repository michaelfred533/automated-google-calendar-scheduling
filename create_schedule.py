"""

"""

from __future__ import print_function
import datetime
from datetime import time
import os.path
import pandas as pd
import logging
import copy
import pytz

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apscheduler.schedulers.background import BackgroundScheduler

from google.oauth2 import service_account

import get_calendar_data


#SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# ----------------------------------------------------------------------------------------------------------------


def helper_create_timezone_datetime_object(time_ISO_string):
    date = datetime.datetime.today().date()
    datetime_string = str(date) + time_ISO_string
    naive_datetime_object = datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
    timezone_datetime_object = pytz.timezone('America/Los_Angeles').localize(naive_datetime_object)

    return timezone_datetime_object

#TODO: add @staticmethod decorator to helper functions 
class Event:
    def __init__(self, topic, duration, study_type):
        self.topic = topic
        self.duration = duration
        self.study_type = study_type
        self.start_time = self.end_time = "pending"

    def __str__(self):
        return f"Topic: {self.topic}, Duration: {self.duration}, Study Type: {self.study_type}"

class MemoryBlockEvent(Event):
    def __init__(self, topic, duration, study_type, study_duration, recall_duration):
        super().__init__(topic, duration, study_type)
        self.study_type = 'memory block'
        self.study_event = Event(self.topic, study_duration, 'study')
        self.recall_event = Event(self.topic, recall_duration, 'recall')       

    def __str__(self):
        return f"MemoryBlockEvent: \n\tTopic: {self.topic}, Duration: {self.duration} \n\tStudy Event: ({self.study_event}) \n\tRecall Event: ({self.recall_event})"
        
def get_user_input():
    """
    get user input for activities and what type of activities they are.
    whether to include free-recall sessions or not
    """
    class HelperUserInput:
        def get_time(self):
            while True:
                total_time = input("How many total hours do you want to spend learning tomorrow? ")
                
                try:
                    total_time = int(total_time)
                except ValueError:
                    continue

                if len(str(total_time)) <= 2:
                    break
                print("Wrong format. Please try again. The expected format is a 1-2 digit whole number.")
            
            total_time = total_time * 60
            return total_time
        def get_topics(self):
            while True:    
                topics = input("Please enter the activities you wish to schedule, seperated by a comma and space. eg. A, B, C: ")
                topics = topics.split(", ")
                if len(set(topics)) == len(topics):
                    break
                print("There are duplicates in your list. Please try again.")

            return topics
        def get_study_type_list(self, topics):
            while True:
                study_type_list = input(f"The activites you chose: {topics}. Please enter the type for each activity (the current types are 'memory' and 'practice'). eg. memory, practice, practice: ")
                study_type_list = study_type_list.lower().split(", ")
                if all(study_type == "memory" or study_type == 'practice' for study_type in study_type_list) and (len(study_type_list) == len(topics)):
                    break
                print("ERROR: study_type_list in unexpected format: ", study_type_list, "Please try again. Make sure the length of the list matches the number of activites entered. You entered ", len(topics), " topics.") 

            return study_type_list
        def get_proportions(self, topics):
            while True:
                proportions = input("Please input the proportion of your total time you'd like to spend for each activity in order separtated by a comma and space. eg. 0.5, 0.25, 0.25: ")
                proportions = [float(prop) for prop in proportions.split(", ")]
                if sum(proportions) == 1.0:
                    break
                print("ERROR: proportions do not add to 1: ", proportions, "Please try again")

            return proportions

    helper = HelperUserInput()

    user_input_info = {}
    user_input_info['total_time'] = helper.get_time()

    while True:
        user_input_info['topics'] = helper.get_topics()
        user_input_info['study_type_list'] = helper.get_study_type_list(user_input_info['topics'])
        user_input_info['proportions'] = helper.get_proportions(user_input_info['topics'])
        
        if len(user_input_info['topics']) == len(user_input_info['proportions']):
            break
        
        print("ERROR: The number of activities and the number of proportions entered do not match. Please try again.")
        print("topics length is ", len(user_input_info['topics']), "and proportions length is ", len(user_input_info['proportions']))

    return user_input_info

class TopicInfo:
    def __init__(self, topic, study_type, proportion, time_remaining):
        self.topic = topic
        self.study_type = study_type
        self.proportion = proportion
        self.time_remaining = time_remaining
        self.events = []

    def __str__(self):
        event_list = "\n".join([str(event) for event in self.events])
        return f"Topic: {self.topic}, Study Type: {self.study_type}, Proportion: {self.proportion}, Time Remaining: {self.time_remaining}\nEvents:\n\t{event_list}"


def initialize_topic_info(user_input_info):
    def calculate_times_for_topics(user_input_info):

        study_times = []
        for prop in user_input_info['proportions']:
            time = round((user_input_info['total_time'] * prop) / 15) * 15 # round time to nearest 15min multiple
            study_times.append(time)

        return study_times
    
    study_times = calculate_times_for_topics(user_input_info)
    
    topic_info_objects = []
    for topic, type, prop, time in zip(user_input_info['topics'], user_input_info['study_type_list'], user_input_info['proportions'], study_times):        
        topic_info_objects.append(TopicInfo(topic, type, prop, time))

    return topic_info_objects


def group_topic_info_by_type(topic_info_objects):

    topic_info_grouped_by_type_dict = {}
    for topic_info in topic_info_objects:
        if topic_info.study_type in topic_info_grouped_by_type_dict.keys():
            topic_info_grouped_by_type_dict[topic_info.study_type].append(topic_info)
        else:
            topic_info_grouped_by_type_dict[topic_info.study_type] = [topic_info]

    return topic_info_grouped_by_type_dict 

def build_events_for_all_topics(topic_info_grouped_by_type_dict):
    """
    input: 
    output:
    """
    #TODO could rewrite this code to support more than 2 types
    for topic_info in topic_info_grouped_by_type_dict['memory']:
        build_events_for_memory_topic(topic_info)

    for topic_info in topic_info_grouped_by_type_dict['practice']:
        build_events_for_practice_topic(topic_info)        

def build_events_for_practice_topic(topic_info):
    """
    input: 
    output: 
    """

    def add_practice_event(topic_info, practice_event_duration):

        event_practice = Event(topic_info.topic, practice_event_duration, topic_info.study_type)
        topic_info.events.extend([event_practice])
        topic_info.time_remaining -= practice_event_duration

    while topic_info.time_remaining > 0:

        if topic_info.time_remaining >= 60:
            add_practice_event(topic_info, 60)

        else:
            add_practice_event(topic_info, topic_info.time_remaining)
    
def build_events_for_memory_topic(topic_info):
    
    def add_memory_block_event(topic_info, memory_block_duration):
            
            recall_duration = 15
            study_duration = memory_block_duration - recall_duration

            memory_block = MemoryBlockEvent(topic_info.topic, memory_block_duration, topic_info.study_type, study_duration, recall_duration)

            topic_info.events.append(memory_block)
            topic_info.time_remaining -= memory_block_duration    
    
    while topic_info.time_remaining > 0:

        if topic_info.time_remaining == 60:
            add_memory_block_event(topic_info, 60)
        
        else:
            memory_block_duration = min(45, topic_info.time_remaining)
            add_memory_block_event(topic_info, memory_block_duration) 
      
        
#TODO probably delete mix_lists function - it's better to sort descending on length      
# def mix_lists(events_1, events_2):
#     """
    
#     """
#     if len(events_1) >= len(events_2):
#         events_long, events_short = events_1, events_2
#     else:
#         events_long, events_short = events_2, events_1 

#     mixed_list = []
#     for event_short, event_long in zip(events_short, events_long):
#         mixed_list.extend([event_long, event_short])

#     length_difference = len(events_long) - len(events_short)
#     if length_difference > 0: 
#         mixed_list.extend(events_long[-length_difference:])


#     print('mixed list: ', mixed_list)
#     return mixed_list
    
#TODO: refactor into smaller functions
def interleave(events):
    """
    """
    #TODO: error handling 
    if len(events) <= 1:
        print('events list is length 1 or 0: ', events)
        raise ValueError
    elif len(events) > 2:
        print('ENTERING recursion: ', events[1:])
        print()
        interleaved_events = interleave(events[1:])
        events = [events[0], interleaved_events] # create new list with interleaved events and leftover events
    
    print('EXITING recursion')

    if len(events[0]) >= len(events[1]):
        events_more, events_less = events[0], events[1]
    else:
        events_more, events_less = events[1], events[0]

    # ensures splits is at least 1
    splits = max(round(len(events_more) / (len(events_less) + 1)), 1)
    print('splits: ', splits)
    
    indexes = [ind for ind in range(splits, len(events_more)) if ind % splits == 0]
    if len(indexes) < len(events_less):
        print('indexes shorter than num of events: ', indexes, 'num events: ', len(events_less))
        indexes.append(len(events_more) + len(events_less) - 1)
    print("indexes: ", indexes)

    final_order_of_events = copy.copy(events_more)
    for ind, event, i in zip(indexes, events_less, range(len(indexes))):
        final_order_of_events.insert(ind + i, event)
    

    print('Interleave results: ')
    for event in final_order_of_events:
        print(event)

    return final_order_of_events

def create_list_of_all_events_to_schedule(topic_info_grouped_by_type_dict):
    
    new_events_list = []
    for study_type_list in topic_info_grouped_by_type_dict.values():
        for topic_info in study_type_list:
            new_events_list.append(topic_info.events)

    return new_events_list



def get_todays_calendar():
    
    start_date = str(datetime.date.today())
    end_date = str((datetime.date.today() + datetime.timedelta(days = 1)))

    service = get_calendar_data.access_calendar(SCOPES)
    events = get_calendar_data.get_events(service, start_date, end_date)
    print('from todays calendar: ', events)

    return events

def add_start_and_end_times_for_events(new_events_list):
   
    def add_start_end_duration_to_existing_events(existing_events):
        for event in existing_events:
            event['start_time'] = pytz.timezone('America/Los_Angeles').localize(datetime.datetime.strptime(event['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S'))
            event['end_time'] = pytz.timezone('America/Los_Angeles').localize(datetime.datetime.strptime(event['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S'))
            event['duration'] = (event['end_time'] - event['start_time']).total_seconds() / 60
    
    def find_non_overlaping_time(existing_events, proposed_new_event_time):
        def update_start_and_end_times(proposed_new_event_time):
            proposed_new_event_time['start'] = existing_event['end_time']
            proposed_new_event_time['end'] = proposed_new_event_time['start'] + datetime.timedelta(minutes = new_event.duration)
            print('updated start time: ', proposed_new_event_time['start'])
            return proposed_new_event_time
        
        for existing_event in existing_events:
            if proposed_new_event_time['start'] < existing_event['end_time'] and proposed_new_event_time['end'] > existing_event['start_time']:
                print('overlap found! proposed start: ', proposed_new_event_time['start'], 'existing event start: ', existing_event['start_time'])
                proposed_new_event_time = update_start_and_end_times(proposed_new_event_time)

        return proposed_new_event_time

    def add_start_and_end_time_to_new_event(new_event, proposed_new_event_time):
            new_event.start_time = proposed_new_event_time['start']
            new_event.end_time = proposed_new_event_time['end']

    proposed_new_event_time = {
        'start': helper_create_timezone_datetime_object('T09:00:00'),
        'end': None
    }
    
    existing_events = get_todays_calendar()
    add_start_end_duration_to_existing_events(existing_events)
    
    schedule = []
    for new_event in new_events_list:
        
        proposed_new_event_time['end'] = proposed_new_event_time['start'] + datetime.timedelta(minutes = new_event.duration)  
        proposed_new_event_time = find_non_overlaping_time(existing_events, proposed_new_event_time)            
        
        add_start_and_end_time_to_new_event(new_event, proposed_new_event_time)
        schedule.append(new_event)
        
        print('added event at this time: ', proposed_new_event_time['start'])
        

        proposed_new_event_time['start'] = proposed_new_event_time['end']

    return schedule 


# TODO: should this be moved to be a nested function?
    # can I change the test script code such that I can use the outer function for adding google calendar events?
    # test add_start_and_end_time_to_new_events4
def create_google_calendar_event(event):

    def add_event_to_google_calendar(event):
        service = get_calendar_data.access_calendar(SCOPES)
        event = service.events().insert(calendarId='primary', body=event).execute()

    event = {
        'summary': event.topic + ' ' + event.study_type,
        'description': 'NA',
        'start': {'dateTime': event.start_time, 'timeZone': "America/Los_Angeles"},
        'end': {'dateTime': event.end_time, 'timeZone': "America/Los_Angeles"},
        'reminders': {
            'useDefault': False,
            'overrides': [],
        },
    }

    add_event_to_google_calendar(event)

#TODO: will need to convert event.start_time / event.end_time back to strings 
def add_events_to_google_calendar(final_order_of_events):
    
    def convert_to_google_format():
        pass

    for event in final_order_of_events:
        print(event.start_time)
        print(event.end_time)





#TODO: make REALLY small funcitons - even 1 line if it improved readability
if __name__ == "__main__":
    # user_input_info = get_user_input()

    # ADDEDADDEDADDEDADDEDADDED
    user_input_info = {
        'total_time' : 180,   
        'topics' : ['A', 'B', 'X'],
        'proportions' : [.33, .33, .34],
        'study_type_list' : ['memory', 'memory', 'practice'], 
    }
    # ADDEDADDEDADDEDADDEDADDED 

    topic_info_objects = initialize_topic_info(user_input_info)

    topic_info_grouped_by_type_dict = group_topic_info_by_type(topic_info_objects)

    build_events_for_all_topics(topic_info_grouped_by_type_dict)
    
    # print("printing topic info....")
    # for topic_info in topic_info_objects:
    #     print(topic_info)

    new_events_list = create_list_of_all_events_to_schedule(topic_info_grouped_by_type_dict)

    #TODO: should be distributed by type AND topic, right now only by topic
    # MAYBE - not sure if this is interleaving or just task-switching
    sorted_topic_list = sorted(new_events_list, key = len, reverse=True)

    final_order_of_events = interleave(sorted_topic_list)
    final_order_of_events = add_start_and_end_times_for_events(final_order_of_events)
    add_events_to_google_calendar(final_order_of_events)



#---------------------------------------


