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

# TODO: this should be moved to test script, because it is only used once in this script
    # adjust function calls in test script too
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

    def set_start_and_end_times(self, start_and_end_times):
        self.start_time = start_and_end_times['start']
        self.end_time = start_and_end_times['end']

    def __str__(self):
        return f"Topic: {self.topic}, Duration: {self.duration}, Study Type: {self.study_type}"

    # TODO: Change the test script code such that I can use the outer function (if I nest this func) for adding google calendar events?
    # test add_start_and_end_time_to_new_events4
    def create_google_calendar_event(self):

        def convert_times_to_google_format():
            '''
            converts event.start_time and event.end_time from dateTime object of format (2023-11-20 T09:00:00-08:00)
            into a string of format (2023-11-20 T09:00:00) which is the format used to create a google calendar event
            '''
            def add_T_to_time_string(time_string):
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

        def add_event_to_google_calendar(event):
            service = get_calendar_data.access_calendar(SCOPES)
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

class MemoryBlockEvent(Event):
    def __init__(self, topic, duration, study_type, study_duration, recall_duration):
        super().__init__(topic, duration, study_type)
        self.study_type = 'memory block'
        self.study_event = Event(self.topic, study_duration, 'study')
        self.recall_event = Event(self.topic, recall_duration, 'recall')       

    def set_start_and_end_times(self, start_and_end_times):
        super().set_start_and_end_times(start_and_end_times)
        self.study_event.start_time = self.start_time
        self.study_event.end_time = self.study_event.start_time + datetime.timedelta(minutes = self.study_event.duration)
        
        # TODO: could add logic to check that the start and end times align with durations etc. 
        self.recall_event.start_time = self.study_event.end_time
        self.recall_event.end_time = self.end_time


    def __str__(self):
        return f"MemoryBlockEvent: \n\tTopic: {self.topic}, Duration: {self.duration} \n\tStudy Event: ({self.study_event}) \n\tRecall Event: ({self.recall_event})"
        
    def create_google_calendar_event(self):
        self.study_event.create_google_calendar_event()
        self.recall_event.create_google_calendar_event()

# TODO: exception handling
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

        memory_block.recall_event.duration = recall_duration
        memory_block.study_event.duration = study_duration

        topic_info.events.append(memory_block)
        topic_info.time_remaining -= memory_block_duration    

    while topic_info.time_remaining > 0:

        if topic_info.time_remaining == 60:
            add_memory_block_event(topic_info, 60)
        
        else:
            memory_block_duration = min(45, topic_info.time_remaining)
            add_memory_block_event(topic_info, memory_block_duration) 
      

def interleave(list_of_each_topics_event_lists):
    """
    """

    def evenly_distribute_events_less_into_events_more(events):
        
        def calculate_number_of_times_to_split_events_more_list(events):
            splits = round(len(events['more']) / (len(events['less']) + 1))
            # ensures at least 1 split
            splits = max(splits, 1)
            print('splits: ', splits)

            return splits
        
        def find_indexes_to_insert_events_less_into_events_more_list(events, splits):

            def add_extra_index_at_end_of_list(events, indexes):
                final_index = len(events['more']) + len(events['less']) - 1
                indexes.append(final_index)

                return indexes
            
            indexes = [ind for ind in range(splits, len(events['more'])) if ind % splits == 0]
            if len(indexes) < len(events['less']):
                print('indexes shorter than num of events: ', indexes, 'num events: ', len(events['less']))
                add_extra_index_at_end_of_list(events, indexes)


            print("indexes: ", indexes)

            return indexes

        splits = calculate_number_of_times_to_split_events_more_list(events)

        indexes = find_indexes_to_insert_events_less_into_events_more_list(events, splits)

        events_in_final_order = copy.copy(events['more'])
        for ind, event, i in zip(indexes, events['less'], range(len(indexes))):
            events_in_final_order.insert(ind + i, event)

        return events_in_final_order
  
    #TODO: error handling 
    if len(list_of_each_topics_event_lists) <= 1:
        print('events list is length 1 or 0: ', list_of_each_topics_event_lists)
        raise ValueError
    elif len(list_of_each_topics_event_lists) > 2:
        print('ENTERING recursion: ', list_of_each_topics_event_lists[1:])
        print()
        interleaved_events = interleave(list_of_each_topics_event_lists[1:])
        list_of_each_topics_event_lists = [list_of_each_topics_event_lists[0], interleaved_events] # create new list with interleaved events and leftover events
    
    print('EXITING recursion')

    events = {
        'more': list_of_each_topics_event_lists[1],
        'less' : list_of_each_topics_event_lists[0],
        }

    events_in_final_order = evenly_distribute_events_less_into_events_more(events)

    print('Interleave results: ')
    for event in events_in_final_order:
        print(event)

    return events_in_final_order

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
        
        new_event.set_start_and_end_times(proposed_new_event_time)
        schedule.append(new_event)
        
        proposed_new_event_time['start'] = proposed_new_event_time['end']

    return schedule 

  
def add_events_to_google_calendar(events_in_final_order):    

    for event in events_in_final_order:
        
        event.create_google_calendar_event()
        

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

    list_of_each_topics_event_lists = create_list_of_all_events_to_schedule(topic_info_grouped_by_type_dict)

    #TODO: should be distributed by type AND topic, right now only by topic
    # MAYBE - not sure if this is interleaving or just task-switching
    sorted_list_of_each_topics_event_lists = sorted(list_of_each_topics_event_lists, key = len, reverse=True)

    events_in_final_order = interleave(sorted_list_of_each_topics_event_lists)
    events_in_final_order = add_start_and_end_times_for_events(events_in_final_order)
    add_events_to_google_calendar(events_in_final_order)



#---------------------------------------


