"""

"""

from __future__ import print_function
import datetime
from datetime import time
import os.path
import pandas as pd
import logging
import copy

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apscheduler.schedulers.background import BackgroundScheduler

from google.oauth2 import service_account

import schedule


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# ----------------------------------------------------------------------------------------------------------------
 
class Event:
    def __init__(self, topic, duration, study_type):
        self.topic = topic
        self.duration = duration
        self.study_type = study_type

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
        

#TODO: create separate function for converting study_type_list?
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

    final_order = copy.copy(events_more)
    for ind, event, i in zip(indexes, events_less, range(len(indexes))):
        final_order.insert(ind + i, event)
    

    print('Interleave results: ')
    for event in final_order:
        print(event)

    return final_order

def create_list_of_events(topic_info_grouped_by_type_dict):
    
    all_events_list = []
    for study_type_list in topic_info_grouped_by_type_dict.values():
        for topic_info in study_type_list:
            all_events_list.append(topic_info.events)

    return all_events_list

def get_todays_calendar():
    
    start_date = str(datetime.date.today())
    end_date = str((datetime.date.today() + datetime.timedelta(days = 2)))

    service = schedule.access_calendar(SCOPES)
    events = schedule.get_events(service, start_date, end_date)

    

    print(events)

#TODO: LEAVING OFF HERE 
def schedule_events(all_events_list):
    
    #date = datetime.today().date()
    date = "2023-10-04"
    next_start_time = datetime.combine(date, time(12,0))
    end_of_day = datetime.combine(date, time(23,0))

    for event in all_events_list:
        start_time = next_start_time
        end_time = start_time + datetime.timedelta(minutes = event.duration)        

    # --- GPT code: 

    # Check for overlapping events
    is_overlap = False
    for event in existing_events:
        if new_event.start_time < event.end_time and new_event.end_time > event.start_time:
            is_overlap = True
            break

    if is_overlap:
        print("Event overlaps with an existing event. Cannot add.")
    else:
        # Add the new event to the calendar
        calendar.add_event(new_event)
        print("Event added to the calendar.")

    # -- END GPT code

# def create_event():

#     # Define the event details
#     event = {
#         'summary': 'Sample Event',
#         'location': 'Sample Location',
#         'description': 'This is a sample event description.',
#         'start': {'dateTime': '2023-10-05T10:00:00', 'timeZone': "America/Los_Angeles"},
#         'end': {'dateTime': '2023-10-05T11:00:00', 'timeZone': "America/Los_Angeles"},
#     }
#     # Insert the event into the primary calendar
#     event = service.events().insert(calendarId='primary', body=event).execute()
#     print('Event created: %s' % (event.get('htmlLink')))



#TODO: make REALLY small funcitons - even 1 line if it improved readability

if __name__ == "__main__":
    # user_input_info = get_user_input()

    # ADDEDADDEDADDEDADDEDADDED
    user_input_info = {}
    user_input_info['total_time'], user_input_info['topics'], user_input_info['proportions'], user_input_info['study_type_list'] = 180, ['A', 'B', 'X'], [.33, .33, .34], ['memory', 'memory', 'practice'] 
    # ADDEDADDEDADDEDADDEDADDED 

    topic_info_objects = initialize_topic_info(user_input_info)

    topic_info_grouped_by_type_dict = group_topic_info_by_type(topic_info_objects)

    build_events_for_all_topics(topic_info_grouped_by_type_dict)
    
    # print("printing topic info....")
    # for topic_info in topic_info_objects:
    #     print(topic_info)


    all_events_list = create_list_of_events(topic_info_grouped_by_type_dict)

    #TODO: should be distributed by type AND topic, right now only by topic
    sorted_topic_list = sorted(all_events_list, key = len, reverse=True)

    final_order = interleave(sorted_topic_list)
 



#---------------------------------------


