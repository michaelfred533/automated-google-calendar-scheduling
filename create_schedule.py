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

def get_user_input():
    """
    get user input for activities and what type of activities they are.
    whether to include free-recall sessions or not
    """

    # input list of activitys and proportion for each activity

    while True:
        total_time = input("How many total hours do you want to spend learning tomorrow? ")
        
        try:
            total_time = int(total_time)
        except ValueError:
            continue

        if len(str(total_time)) <= 2:
            break
        print("Wrong format. Please try again. The expected format is a 1-2 digit whole number.")
    
    while True:
        while True:    
            subject_list = input("Please enter the activities you wish to schedule, seperated by a comma and space (A, B, C): ")
            subject_list = subject_list.split(", ")
            if len(set(subject_list)) == len(subject_list):
                break
            print("There are duplicates in your list. Please try again.")

        while True:
            memorize_list = input(f"The activites you chose: {subject_list}. Please enter 'Y' or 'N' for each activity depending on if it involves memorization (Y, N, Y): ")
            memorize_list = memorize_list.lower().split(", ")
            if all(mem == "y" or mem == 'n' for mem in memorize_list) and (len(memorize_list) == len(subject_list)):
                break
            print("ERROR: memorize_list in unexpected format: ", memorize_list, "Please try again. Make sure the length of the list matches the number of activites entered. You entered ", len(subject_list), " subjects.") 

        while True:
            proportion_list = input("Please input the proportion of your total time you'd like to spend for each activity in order separtated by a comma and space: (.5, .25, .25): ")
            proportion_list = [float(prop) for prop in proportion_list.split(", ")]
            if sum(proportion_list) == 1.0:
                break
            print("ERROR: proportions do not add to 1: ", proportion_list, "Please try again")

        if len(subject_list) == len(proportion_list):
            break
        
        print("ERROR: The number of activities and the number of proportions entered do not match. Please try again.")
        print("subject_list length is ", len(subject_list), "and proportion_list length is ", len(proportion_list))
            
    
    subject_list_mem = []
    subject_list_nonmem = []
    print(memorize_list)
    for sub, mem, prop in zip(subject_list, memorize_list, proportion_list):
        print('mem: ', mem)
        if mem == "n":
             subject_list_nonmem.append((sub, prop))
        elif mem == "y":
            subject_list_mem.append((sub, prop))
        else: print("mem in unexpected format: ", mem) # NOTE: this line should never fire because of the earlier check

    total_time = total_time * 60 # convert to minutes

    return total_time, subject_list_mem,  subject_list_nonmem 


def calc_time_mem(time_mem, subject_list_mem,  proportion_list_mem):
    """
    input: 
        time_mem: amount of time to study memorization topics in minutes
        subject_list: list of activities to be done
        proportion_list_mem: proportion of each subject to be done
    
    output: events in 15m increments to schedule
    """

    time_for_subject_list = []
    for prop in proportion_list_mem:
        time = round((time_mem * prop) / 15) * 15 # round time to nearest 15min multiple
        time_for_subject_list.append(time)

            
    # add logic to filter through which kind of event
    # if free-recall:
    # create list of events in order
    
    all_events_list = []
    for time, subject in zip(time_for_subject_list, subject_list_mem):
        print()
        print("time and subject: ", time, subject)
        event_list = []
        time_copy = copy.copy(time)
        while time_copy > 0:
            if time_copy == 15 or time_copy == 30: # if 15 or 30m remaining, insert only study time
                print('Last 15m or 30m chunk:', time_copy)
                event_study = {
                    'name' : (subject + " study"),
                    'duration' : time_copy,
                    }
                event_list.append(event_study)
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
                event_list.extend([event_study, event_recall])
                time_copy -= 45
        print('mem study Event_list: ---- ', event_list)
        all_events_list.append(event_list) 

    return all_events_list


def calc_time_nonmem(time_nonmem,  subject_list_nonmem, proportion_list_nonmem):
    """
    input: 
    time_nonmem: amount of time to practice the subject
    subject_list: list of activities to be done
    proportion_list_nonmem: proportion of each subject to be done
    
    output: events in 15m increments to schedule
    """

    time_for_subject_list = []
    for prop in proportion_list_nonmem:
        time = round((time_nonmem * prop) / 15) * 15 # round time to nearest 15min multiple
        time_for_subject_list.append(time)

            
    # add logic to filter through which kind of event
    # if free-recall:
    # create list of events in order
    
    all_events_list = []
    for time, subject in zip(time_for_subject_list, subject_list_nonmem):
        print()
        print("time and subject: ", time, subject)
        event_list = []
        time_copy = copy.copy(time)

        while time_copy > 0:

            if time_copy >= 60:
                print('time greater than 60:', time_copy)
                event_practice = {
                    'name' : (subject + " practice"),
                    'duration' : 60,
                    }
                event_list.extend([event_practice])
                time_copy -= 60

            else:
                print('Last chunk under 1 hour: ', time_copy)
                event_practice = {
                    'name' : (subject + " practice"),
                    'duration' : time_copy,
                    }
                event_list.append(event_practice)
                time_copy = 0

        print('Nonmem Practice Event_list: ---- ', event_list)
        all_events_list.append(event_list) 

    return all_events_list

#def calc_time():

#def event_nonrem():

#def event_rem():


if __name__ == "__main__":
    total_time, subject_list_mem,  subject_list_nonmem = get_user_input()
    # events_list_mem = calc_time_mem(3, ["A", "B", "C"], [.5, .25, .25]) 
    # print()
    # print(events_list_mem)


    ## LEAVING OFF HERE, CREATE NEXT FUNCTION THAT INTERLEAVES THE STUDY BLOCKS 
    # TODO: create another function to be called within the for-loop for the nonmen and mem events function


"""
steps:

# define hours of day when study blocks can be input
# interleave practice blocks
# schedule around pre-existing events
# set total study time per day
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


