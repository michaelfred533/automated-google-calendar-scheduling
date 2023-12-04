"""

"""

from __future__ import print_function # must be at beginning of file

# 3rd party imports
import pytz

# python built-in imports
import copy
from dataclasses import dataclass, field
import datetime
from datetime import time
from typing import List, Dict

# local imports
import get_calendar_data
from exceptions import * # imports all exception classes into current namespace, such that you don't have to call exceptions.MyError each time. This is usually a bad idea though, as names can overlap quickly in large projects


#SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# ----------------------------------------------------------------------------------------------------------------

def helper_create_timezone_datetime_object(time_ISO_string: str) -> datetime.datetime:
    """
    converts a time in string format into a datetime object w/ timezone to be used to compare with other datetime objects
    """
    
    date = datetime.datetime.today().date()
    datetime_string = str(date) + time_ISO_string
    naive_datetime_object = datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
    timezone_datetime_object = pytz.timezone('America/Los_Angeles').localize(naive_datetime_object)

    return timezone_datetime_object

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

def get_user_input() -> dict:
    """
    get user input for activities and what type of activities they are.
    whether to include free-recall sessions or not
    """
    class UserInputValidation:
        
        @staticmethod
        def get_time():
            
            while True:
                total_time = input("How many total hours do you want to spend learning tomorrow? ")
                
                try:
                    total_time = float(total_time)
                    if total_time >= 15: # time to study should be less than 15 hours
                        raise TooMuchStudyTimeError
                except ValueError:
                    print("Error: Please enter a number.")
                except TooMuchStudyTimeError:
                    print("Error: Please enter less than 15 hours.")
                except Exception:
                    print('Error: Something is wrong with the input information. Please try again.')
                
                else:
                    break
                
            total_time = total_time * 60
            return total_time
        
        @staticmethod
        def get_topics():
            
            while True:    
                topics = input("Please enter the activities you wish to schedule, seperated by a comma and space. eg. A, B, C: ")

                try:
                    if ", " not in topics:
                        raise MissingCommaError
                    topics = topics.split(", ")
                    if len(topics) >= 10:
                        raise TooManyTopicsError
                    if len(set(topics)) != len(topics):
                        raise DuplicateTopicsError
                
                except MissingCommaError:
                    print('Error: Please separate study activitys by a comma and space.')
                except TooManyTopicsError:
                    print('Error: You entered too many topics. Please enter less than 10 topics.')
                except DuplicateTopicsError:
                    print("Error: There are duplicates in your list. Please try again.")
                except Exception:
                    print('Error: Something is wrong with the input information. Please try again.')


                else:
                    break


            return topics
        
        @staticmethod
        def get_study_type_list(topics):

            while True:
                print(f"The activites you chose: {topics}.")
                study_type_list = input("Please enter the type for each activity (the current types are 'memory' and 'practice'). eg. memory, practice, practice: ")

                try:
                    if ", " not in study_type_list:
                        raise MissingCommaError
                    study_type_list = study_type_list.lower().split(", ")
                    if len(study_type_list) != len(topics):
                        raise LengthMismatchError
                    if not all(study_type == 'memory' or study_type == 'practice' for study_type in study_type_list):
                        raise IncorrectTypeError

                except MissingCommaError:
                    print("Error: Please enter each study type separated by a comma and space.")
                except LengthMismatchError:
                    print("Error: The length of the entered list does not match the length of the topics list.")
                except IncorrectTypeError:
                    print("Error: One or more of the types you entered does not match the supported types.")
                except Exception:
                    print('Error: Something is wrong with the input information. Please try again.')

                else: 
                    break

            return study_type_list
        
        @staticmethod
        def get_proportions(topics):
            while True:
                print(f"The activites you chose: {topics}.")
                proportions = input("Please input the proportion of your total time you'd like to spend for each activity in order separtated by a comma and space. eg. 0.5, 0.25, 0.25: ")
                
                try:
                    if ", " not in proportions:
                        raise MissingCommaError
    
                    proportions = [float(prop) for prop in proportions.split(", ")]
                    if len(proportions) != len(topics):
                        raise LengthMismatchError
                    if sum(proportions) != 1.0:
                        raise ProportionsDontAddToOneError
                except MissingCommaError:
                    print('Error: Please separate proportions by a comma and space.')
                except ValueError:
                    print('Error: Please enter numbers only.')
                except LengthMismatchError:
                    print('Error: The number of proportions does not match the number of topics entered.')
                except ProportionsDontAddToOneError:
                    print("Error: proportions do not add to 1: ", proportions)
                except Exception:
                    print('Error: Something is wrong with the input information. Please try again.')

                else:
                    break

            return proportions

    user_input_info = {}

    user_input_info['total_time'] = UserInputValidation.get_time()
    user_input_info['topics'] = UserInputValidation.get_topics()
    user_input_info['study_type_list'] = UserInputValidation.get_study_type_list(user_input_info['topics'])
    user_input_info['proportions'] = UserInputValidation.get_proportions(user_input_info['topics'])
    
    return user_input_info

@dataclass
class TopicInfo:
    topic: str
    study_type: str
    proportion: float
    time_remaining: int
    events: list = field(default_factory=list) # No defualt mutable arguments allowed, use default_factory instead

    def __str__(self):
        event_list = "\n".join([str(event) for event in self.events])
        return f"Topic: {self.topic}, Study Type: {self.study_type}, Proportion: {self.proportion}, Time Remaining: {self.time_remaining}\nEvents:\n\t{event_list}"


def initialize_topic_info(user_input_info: dict) -> List[TopicInfo]:
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


def group_topic_info_by_type(topic_info_objects: List[TopicInfo]) -> Dict[str, List[TopicInfo]]:

    topic_info_grouped_by_type_dict = {}
    for topic_info in topic_info_objects:
        if topic_info.study_type in topic_info_grouped_by_type_dict.keys():
            topic_info_grouped_by_type_dict[topic_info.study_type].append(topic_info)
        else:
            topic_info_grouped_by_type_dict[topic_info.study_type] = [topic_info]

    return topic_info_grouped_by_type_dict 

def build_events_for_all_topics(topic_info_grouped_by_type_dict: Dict[str, List[TopicInfo]]) -> None:
    """
    input: 
    output:
    """
    # NOTE: Could rewrite this code to support more than 2 types

    for topic_type in topic_info_grouped_by_type_dict.keys():
        if topic_type == 'memory':
            for topic_info in topic_info_grouped_by_type_dict['memory']:
                build_events_for_memory_topic(topic_info)
        elif topic_type == 'practice':
            for topic_info in topic_info_grouped_by_type_dict['practice']:
                build_events_for_practice_topic(topic_info)
        else:
            raise Exception        

def build_events_for_practice_topic(topic_info: TopicInfo) -> None:
    """
    input: 
    output: 
    """

    def add_practice_event(topic_info, practice_event_duration):

        event_practice = Event(topic_info.topic, practice_event_duration, topic_info.study_type)
        topic_info.events.extend([event_practice])
        topic_info.time_remaining -= practice_event_duration

    while topic_info.time_remaining > 0:

        if topic_info.time_remaining >= 90:
            add_practice_event(topic_info, 90)

        else:
            add_practice_event(topic_info, topic_info.time_remaining)
    
def build_events_for_memory_topic(topic_info: TopicInfo) -> None:
    
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
      


def create_list_of_all_events_to_schedule(topic_info_grouped_by_type_dict: Dict[str, List[TopicInfo]]) -> List[List[Event]]:
    
    list_of_each_topics_event_lists = []
    for study_type_list in topic_info_grouped_by_type_dict.values():
        for topic_info in study_type_list:
            list_of_each_topics_event_lists.append(topic_info.events)

    return list_of_each_topics_event_lists


def interleave(list_of_each_topics_event_lists: List[List[Event]]) -> List[Event]:
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
    

   
    if len(list_of_each_topics_event_lists) > 2:
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

def get_todays_calendar() -> List[dict]:
    
    start_date = str(datetime.date.today())
    end_date = str((datetime.date.today() + datetime.timedelta(days = 1)))

    service = get_calendar_data.access_calendar(SCOPES)
    events = get_calendar_data.get_events(service, start_date, end_date)
    print('from todays calendar: ', events, '\n')

    return events

def add_start_and_end_times_for_events(new_events_list: List[Event]) -> None:
   
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


def add_events_to_google_calendar(events_in_final_order: List[Event]) -> None:    

    for event in events_in_final_order:
        event.create_google_calendar_event()
        


def skip_unnecessary_steps(topic_info_objects: List[TopicInfo]) -> List[Event]:
    events_in_final_order = topic_info_objects[0].events

    return events_in_final_order

def run_program(user_input_info: Dict) -> None:
    topic_info_objects = initialize_topic_info(user_input_info)
    topic_info_grouped_by_type_dict = group_topic_info_by_type(topic_info_objects)
    build_events_for_all_topics(topic_info_grouped_by_type_dict)

    number_of_different_topics = len(topic_info_grouped_by_type_dict.keys())
    if  number_of_different_topics == 1:
        print('only 1 topic')
        events_in_final_order = skip_unnecessary_steps(topic_info_objects)
    else:
        list_of_each_topics_event_lists = create_list_of_all_events_to_schedule(topic_info_grouped_by_type_dict)
        sorted_list_of_each_topics_event_lists = sorted(list_of_each_topics_event_lists, key = len, reverse=True)
        events_in_final_order = interleave(sorted_list_of_each_topics_event_lists)
    
    add_start_and_end_times_for_events(events_in_final_order)
    add_events_to_google_calendar(events_in_final_order)

if __name__ == "__main__":

    user_input_info = get_user_input()
    run_program(user_input_info)

    # NOTE: Could distribute by type AND topic, right now only by topic
    # MAYBE - not sure if this is interleaving or just task-switching

