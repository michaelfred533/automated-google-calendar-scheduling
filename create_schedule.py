"""

"""

from __future__ import print_function
import datetime
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

# -------------------------------------------------------------------------

# service = schedule.access_calendar(SCOPES)


# logging.basicConfig(level = logging.DEBUG)

# start_date = str(datetime.date.today())
# end_date = str((datetime.date.today() + datetime.timedelta(days = 2)))
# logging.info(f"start date is {start_date}")
# logging.info(f"end date is {end_date}")
# events = schedule.get_events(service, start_date, end_date)
# print(len(events), events[0])

# ----------------------------------------------------------------------------------------------------------------

#TODO: fill out this class 
class event:

    def set_duration():
        pass
    def get_duration():
        pass
    def set_name():
        pass
    def get_name():
        pass 
    def set_session_type():
        pass
    def get_session_type():
        pass 
class recall(event):
    
    pass
class practice(event):
    def __init__(self, subject, duration):
        self.duration = duration
        self.subject = subject

    pass 


def get_user_input():
    """
    get user input for activities and what type of activities they are.
    whether to include free-recall sessions or not
    """
    helper = HelperUserInput()

    total_time = helper.get_time()

    while True:
        subjects = helper.get_subjects()
        memorize_or_not_list = helper.get_memorize_or_not_list(subjects)
        proportions = helper.get_proportions(subjects)
        
        if len(subjects) == len(proportions):
            break
        
        print("ERROR: The number of activities and the number of proportions entered do not match. Please try again.")
        print("subjects length is ", len(subjects), "and proportions length is ", len(proportions))

    return total_time, subjects, proportions, memorize_or_not_list

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
        return total_time
    def get_subjects(self):
        while True:    
            subjects = input("Please enter the activities you wish to schedule, seperated by a comma and space. eg. A, B, C: ")
            subjects = subjects.split(", ")
            if len(set(subjects)) == len(subjects):
                break
            print("There are duplicates in your list. Please try again.")

        return subjects
    def get_memorize_or_not_list(self, subjects):
        while True:
            memorize_or_not_list = input(f"The activites you chose: {subjects}. Please enter 'Y' or 'N' for each activity depending on if it involves memorization. eg. Y, N, Y: ")
            memorize_or_not_list = memorize_or_not_list.lower().split(", ")
            if all(mem == "y" or mem == 'n' for mem in memorize_or_not_list) and (len(memorize_or_not_list) == len(subjects)):
                break
            print("ERROR: memorize_or_not_list in unexpected format: ", memorize_or_not_list, "Please try again. Make sure the length of the list matches the number of activites entered. You entered ", len(subjects), " subjects.") 

        return memorize_or_not_list
    def get_proportions(self, subjects):
        while True:
            proportions = input("Please input the proportion of your total time you'd like to spend for each activity in order separtated by a comma and space. eg. 0.5, 0.25, 0.25: ")
            proportions = [float(prop) for prop in proportions.split(", ")]
            if sum(proportions) == 1.0:
                break
            print("ERROR: proportions do not add to 1: ", proportions, "Please try again")

        return proportions



def calc_times(total_time, subjects, proportions):

    #subjects, proportions = zip(*[(tup[0], tup[1]) for tup in subject_proportion_tuples])

    total_time = total_time * 60 # convert hours to minutes

    subject_time_tuples = []
    for sub, prop in zip(subjects, proportions):
        time = round((total_time * prop) / 15) * 15 # round time to nearest 15min multiple
        
        subject_time_tuples.append((sub, time))
    
    return subject_time_tuples

def separate(subject_time_tuples, memorize_or_not_list):

    subject_time_tuples_mem = []
    subject_time_tuples_nonmem = []
    for tup, mem in zip(subject_time_tuples, memorize_or_not_list):
        
        if mem == "n":
            subject_time_tuples_nonmem.append(tup)
        elif mem == "y":
            subject_time_tuples_mem.append(tup)
        else: print("mem in unexpected format: ", mem) # NOTE: this line should never fire because of the earlier check

    return subject_time_tuples_mem,  subject_time_tuples_nonmem 


#TODO passing in boolean to function is bad practice, fix this method
def calc_events(self, subject_time_tuples, is_mem):
    """
    input: 
    

    output: events in 15m increments to schedule
    """

    all_events_list = []
    for tup in subject_time_tuples:
        print("current tup: ", tup)
        if is_mem:
            events = calc_event.helper_calc_event_mem(tup[0], tup[1])
        else:
            events = calc_event.helper_calc_event_nonmem(tup[0], tup[1])
        all_events_list.extend([events]) 

    return all_events_list

class HelperCalcEvents():

    #TODO create new sub-functions under calc_event Class 
    def mem(self, subject, time):
        """
        input: 
        time: amount of time to practice the subject
        subject: the activity to create calculate time-blocks
        
        output: events in 15m increments to schedule
        """
        events = []
        time_copy = copy.copy(time) 
        events = []
        time_copy = copy.copy(time)
        while time_copy > 0:
            if time_copy == 15:
                print('last 15m chunk, add to previous recall block')
                if events:
                    events[-1]['duration'] += 15
                    events[-1]['recall block'][0]['duration'] += 15
                elif not events:
                    event_study = {
                    'name' : (subject + " study"),
                    'duration' : time_copy,
                    }
                    events.append(event_study)
                time_copy = 0
            elif time_copy == 30: # if 30m remaining, insert only study time
                print('last 30m chunk:', time_copy)
                event_study = {
                    'name' : (subject + " study"),
                    'duration' : time_copy,
                    }
                events.append(event_study)
                time_copy = 0

            elif time_copy >= 45:
                print('time greater than 45:', time_copy)
                event_study = {
                    'name' : (subject + " study"),
                    'duration' : 30,
                    }
                event_recall = {
                    'name' : (subject + " recall"),
                    'duration' : 15,
                    }
                recall_block = {'recall block' : [event_study, event_recall], 'duration' : 45}
                events.append(recall_block)
                time_copy -= 45
            
        return events

    def nonmem(self, subject, time):
        """
        input: 
        time: amount of time to practice the subject
        subject: the activity to create calculate time-blocks
        

        output: 

        """
        events = []
        time_copy = copy.copy(time)

        while time_copy > 0:

            if time_copy >= 60:
                print('time greater than 1 hour:', time_copy)
                event_practice = {
                    'name' : (subject + " practice"),
                    'duration' : 60,
                    }
                events.extend([event_practice])
                time_copy -= 60

            else:
                print('Last chunk under 1 hour: ', time_copy)
                event_practice = {
                    'name' : (subject + " practice"),
                    'duration' : time_copy,
                    }
                events.append(event_practice)
                time_copy = 0
        
        return events

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
    

#TODO break this up into smaller functions 
def interleave(events):
    """
    this function will actually be used to interleave nonmem and mem items 
    amongst themselves and then again to merge together
    """
    if len(events) <= 1:
        print('events list is length 1 or 0: ', events)
        raise ValueError
    elif len(events) > 2:
        print('ENTERING recursion: ', events[1:])
        print()
        interleaved_events = interleave(events[1:])
        events = [events[0], interleaved_events] # create new list with interleaved events and leftover events
    
    print('EXITING recursion')
    events_1, events_2 = events[0], events[1]

    if len(events_1) >= len(events_2):
        events_more, events_less = events_1, events_2
    else:
        events_more, events_less = events_2, events_1

    splits = round(len(events_more) / (len(events_less) + 1))
    if splits == 0:
        print('changing splits from 0 to 1..')
        splits = 1
    print('splits: ', splits)
    
    indexes = [ind for ind in range(splits, len(events_more)) if ind % splits == 0]
    if len(indexes) < len(events_less):
        print('indexes shorter than num of events: ', indexes, 'num events: ', len(events_less))
        indexes.append(len(events_more) + len(events_less) - 1)
    print("indexes: ", indexes)

    final_order = copy.copy(events_more)
    for ind, event, i in zip(indexes, events_less, range(len(indexes))):
        final_order.insert(ind + i, event)
    

    print('Interleave results: ', final_order)
    return final_order


# user_input -> calc_times -> separate -> calc_events -> interleave

if __name__ == "__main__":
    total_time, subjects, proportions, memorize_or_not_list = get_user_input()
    print(total_time, subjects, proportions, memorize_or_not_list)
    
    # # ADDED
    # total_time, subjects, proportions, memorize_or_not_list = 8, ['A', 'B', 'X'], [.175, .175, .75], ['y', 'y', 'n'] 
    # # ADDED

    # subject_time_tuples = calc_times(total_time, subjects, proportions)
    # subject_time_tuples_mem,  subject_time_tuples_nonmem = separate(subject_time_tuples, memorize_or_not_list)

    # events_mem = calc_event.calc_events(subject_time_tuples_mem, is_mem = 1)
    # events_nonmem = calc_event.calc_events(subject_time_tuples_nonmem, 0)
    # print("both event sets before interleaving: ")
    # print(events_mem)
    # print(events_nonmem)

    # sorted_subject_list = sorted(events_mem + events_nonmem, key = len, reverse=True)

    # final_order = interleave(sorted_subject_list)



    ## LEAVING OFF HERE: 
    # go through and create classes and more sub-functions. (<30 lines per func)
    # create checks for only 1 type of study
    # create checks for 1 subject 


"""
notes:

if you want to change how different mem subjects and non-mem subjects are dispursed, 
tweak the more/less logic flow in interleave() function 

"""








# def create_events():

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


