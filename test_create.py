"""
test the function of create_schedule.py
"""
import datetime
from datetime import time
import pytz

import unittest
from unittest import mock

import create_schedule
import get_calendar_data

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


#TODO: refactor code into helper functions 

class Helpers:
      
    #TODO: maybe delete this method. Or if keeping it, replace -07:00 with LA timezone via pytz 
    @staticmethod
    def create_sample_event(start_time, end_time):
        # format: 'T11:30:00-07:00'
        date = str(datetime.date.today())
        existing_event = {'start' : {'dateTime' : date + start_time}, 'end' : {'dateTime' : date + end_time}}
        return existing_event

    @staticmethod
    def assertEqual_all_attriubutes(event_expected, event_result):
        
        attributes_expected = [attr for attr in dir(event_expected) if not callable(getattr(event_expected, attr)) and not attr.startswith("__")]
        attributes_result = [attr for attr in dir(event_result) if not callable(getattr(event_result, attr))and not attr.startswith("__")]
        for attr_name in attributes_expected:
            attr_expected = getattr(event_expected, attr_name)
            attr_result = getattr(event_result, attr_name)
            print('attr_expected', attr_expected)
            print('attr_result', attr_result)
            assert attr_expected == attr_result, f"attributes do not match. Expected: {attr_expected}, Result: {attr_result}"


#TODO: separate into separate classes
class test_create(unittest.TestCase):

    # def test_mix_lists(self):

    #     # input:
    #     events_1, events_2 = ['A', 'B'], ['W', 'X', 'Y', 'Z']
        
    #     # result:
    #     result = create_schedule.mix_lists(events_1, events_2)

    #     # expected:
    #     expected = ['W', 'A', 'X', 'B', 'Y', 'Z']

    #     # tests:
    #     self.assertEqual(result, expected)
    #     self.assertEqual(len(result), (len(events_1) + len(events_2)))
    # def test_mix_lists2(self):

    #     # input:
    #     events_1, events_2 = ['A', 'B'], ['W', 'X', 'Y']
        
    #     # result:
    #     result = create_schedule.mix_lists(events_1, events_2)

    #     # expected:
    #     expected = ['W', 'A', 'X', 'B', 'Y']

    #     # tests:
    #     self.assertEqual(result, expected)
    #     self.assertEqual(len(result), (len(events_1) + len(events_2)))    
   
    ## ------------------------End of test block---------------------

    ## ------------------------End of test block---------------------

  
    def test_get_todays_calendar(self):

        start_date = "2023-10-04"
        end_date = "2023-10-06" 

        service = get_calendar_data.access_calendar(SCOPES)
        events = get_calendar_data.get_events(service, start_date, end_date)

        #print(events)
        #events[0]['start']['dateTime']
        print(type(events[0]['start']['dateTime']))


    # 1 and 2 use mock.patch to mock get_todays_calendar
    def test_schedule_times_for_events1(self):
        # input:

        date = str(datetime.date.today())
        existing_events = [
            {'start' : {'dateTime' : date + 'T10:00:00-07:00'}, 'end' : {'dateTime' : date + 'T11:30:00-07:00'}},
            {'start' : {'dateTime' : date + 'T11:30:00-07:00'}, 'end' : {'dateTime' : date + 'T12:30:00-07:00'}},
            ]
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            result = create_schedule.schedule_times_for_events(new_events)
        print('mock shedule: ', result)
        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        event1.start_time, event1.end_time = create_schedule.helper_create_timezone_datetime_object('T09:00:00'), create_schedule.helper_create_timezone_datetime_object('T10:00:00') 
        event2.start_time, event2.end_time = create_schedule.helper_create_timezone_datetime_object('T12:30:00'), create_schedule.helper_create_timezone_datetime_object('T13:30:00') 

        expected = [event1, event2]

        # tests: 
        # check that each attribute matches for each event in the schedule
        for event_expected, event_result in zip(expected, result):
            Helpers.assertEqual_all_attriubutes(event_expected, event_result)

    def test_schedule_times_for_events2(self):
        # input:

        date = str(datetime.date.today())
        existing_events = [
            {'start' : {'dateTime' : date + 'T09:00:00-07:00'}, 'end' : {'dateTime' : date + 'T10:30:00-07:00'}},
            {'start' : {'dateTime' : date + 'T11:30:00-07:00'}, 'end' : {'dateTime' : date + 'T12:00:00-07:00'}},
            ]
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            result = create_schedule.schedule_times_for_events(new_events)
        print('mock shedule: ', result)

        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        event1.start_time, event1.end_time = create_schedule.helper_create_timezone_datetime_object('T10:30:00'), create_schedule.helper_create_timezone_datetime_object('T11:30:00') 
        event2.start_time, event2.end_time = create_schedule.helper_create_timezone_datetime_object('T12:00:00'), create_schedule.helper_create_timezone_datetime_object('T13:00:00') 

        expected = [event1, event2]
        
        # tests: 
        # check that each attribute matches for each event in the schedule
        for event_expected, event_result in zip(expected, result):
           Helpers.assertEqual_all_attriubutes(event_expected, event_result)

    # 3 adds actual test event to the calendar
    def test_schedule_times_for_events3(self):
         # add test events to google calendar:
        date = str(datetime.date.today())
        event_to_add = create_schedule.Event('A', 60, 'practice')
        event_to_add.start_time, event_to_add.end_time = date + 'T10:30:00', date + 'T11:00:00'
        create_schedule.create_google_calendar_event(event_to_add)
       
        # input:
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        result = create_schedule.schedule_times_for_events(new_events)

        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        
        event1.start_time, event1.end_time = create_schedule.helper_create_timezone_datetime_object('T09:00:00'), create_schedule.helper_create_timezone_datetime_object('T10:00:00') 
        event2.start_time, event2.end_time = create_schedule.helper_create_timezone_datetime_object('T11:00:00'), create_schedule.helper_create_timezone_datetime_object('T12:00:00') 

        expected = [event1, event2]

        # tests: 
        for event_expected, event_result in zip(expected, result):
            Helpers.assertEqual_all_attriubutes(event_expected, event_result)

    #----------------------End of test block---------------------
    
    def test_create_google_calendar_event(self):
        
        #input:         
        input_event = create_schedule.Event('A', 60, 'practice')

        date = str(datetime.date.today())
        input_event.start_time = date + 'T09:00:00'
        input_event.end_time = date + 'T10:00:00'

        create_schedule.create_google_calendar_event(input_event)
        
        # Confirm that the event was created
        events_from_calendar = create_schedule.get_todays_calendar()
        
        #tests: 
        self.assertTrue(events_from_calendar != None)
        self.assertTrue(events_from_calendar != [])
        self.assertTrue(events_from_calendar[0]['start']['dateTime'][:-6] == input_event.start_time)

    #----------------------End of test block---------------------


    def test_interleave1(self):
        # input:
        len_1, len_2 = 1, 4
        events_1 = ['A'] * len_1
        events_2 = ['B'] * len_2
        events = [events_1, events_2]

        # result:
        result = create_schedule.interleave(events)
        # expected: 
        expected = ['B', 'B', 'A', 'B', 'B']

        # tests:
        self.assertEqual(len(result), (len(events_1) + len(events_2)))
        self.assertEqual(result, expected)

    def test_interleave2(self):
        # input:
        len_1, len_2, len_3 = 1, 2, 3
        events_1 = ['A'] * len_1
        events_2 = ['B'] * len_2
        events_3 = ['C'] * len_3 
        events = [events_1, events_2, events_3]

        # result:
        result = create_schedule.interleave(events)
        # expected: 
        expected = ['C', 'B', 'A', 'C', 'B', 'C']

        # tests:
        self.assertEqual(result, expected)

    def test_interleave3(self):
        # input:
        lens = [2, 2, 4, 4, 5] 
        events_1 = ['A'] * lens[0]
        events_2 = ['B'] * lens[1]
        events_3 = ['X'] * lens[2]
        events_4 = ['Y'] * lens[3]
        events_5 = ['Z'] * lens[4]

        events = sorted([events_1, events_2, events_3, events_4, events_5], key=len, reverse = True)
        print(events)

        # result:
        result = create_schedule.interleave(events)

        # tests:
        subject_list = ['A', 'B', 'X', 'Y', 'Z']
        # makes sure that each element is maximally distributed 
        for subject in subject_list:
            indexes = [index for index, value in enumerate(result) if value == subject]
            distances_from_same_subject =[]
            for i in range(len(indexes)-1):
                distances_from_same_subject.append(indexes[i+1] - indexes[i])
            for i in range(len(distances_from_same_subject)-1):
                self.assertTrue(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]) <= 1)
                print(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]))
        
    def test_interleave4(self):
        # input:
        lens = [2, 2, 1] 
        events_1 = ['A'] * lens[0]
        events_2 = ['B'] * lens[1]
        events_3 = ['X'] * lens[2]

        events = sorted([events_1, events_2, events_3], key=len, reverse = True)
        print(events)

        # result:
        result = create_schedule.interleave(events)

        # tests:
        subject_list = ['A', 'B', 'X']
        
        #TODO: replace w/ helper function
        # makes sure that each element is maximally distributed 
        for subject in subject_list:
            indexes = [index for index, value in enumerate(result) if value == subject] # gets all indexes for given subject
            distances_from_same_subject =[] 
            for i in range(len(indexes)-1):
                distances_from_same_subject.append(indexes[i+1] - indexes[i])
            for i in range(len(distances_from_same_subject)-1):
                self.assertTrue(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]) <= 1)
                print(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]))

    # TODO: MAYBE delete this test
    # create test for maximizing topic AND type distances 
    def test_interleave_by_study_type(self):
            # input:
            lens = [1, 1, 1]
            eventA = create_schedule.Event('A', 60, 'type 1')
            eventB = create_schedule.Event('B', 60, 'type 1')
            eventX = create_schedule.Event('X', 60, 'type 2')

            events_1 = [eventA] * lens[0]
            events_2 = [eventB] * lens[1]
            events_3 = [eventX] * lens[2]

            events = sorted([events_1, events_2, events_3], key=len, reverse = True)
            print(events)

            # result:
            result = create_schedule.interleave(events)

            # tests:
            subject_list = ['A', 'B', 'X']
            
            #TODO: replace w/ helper function
            # makes sure that each element is maximally distributed 
            
            # for subject in subject_list:
            #     indexes = [index for index, value in enumerate(result) if value == subject] # gets all indexes for given subject
            #     distances_from_same_subject =[] 
            #     for i in range(len(indexes)-1):
            #         distances_from_same_subject.append(indexes[i+1] - indexes[i])
            #     for i in range(len(distances_from_same_subject)-1):
            #         self.assertTrue(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]) <= 1)
            #         print(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]))





        ## ------------------------End of test block---------------------

    #----------------------End of test block---------------------

    def test_build_events_for_memory_topic1(self):
        # Create a mock TopicInfo instance for testing
        topic_info = create_schedule.TopicInfo("Test Topic", "study", 1, 60)

        # Call the function to be tested
        create_schedule.build_events_for_memory_topic(topic_info)

        # Assert the changes made by the function
        print(topic_info.events)
        self.assertEqual(len(topic_info.events), 1)  # Check if two events are added

        # Assert that the added events are MemoryBlockEvent instances
        for event in topic_info.events:
            self.assertTrue(isinstance(event, create_schedule.MemoryBlockEvent))

    def test_build_events_for_memory_topic2(self):
        # Create a mock TopicInfo instance for testing
        proportion = 1
        time_remaining = 90
        topic_info = create_schedule.TopicInfo("Test Topic", "study", proportion, time_remaining)

        # Call the function to be tested
        create_schedule.build_events_for_memory_topic(topic_info)

        # Assert the changes made by the function
        self.assertEqual(len(topic_info.events), 2)  # Check if two events are added

        # Assert that the added events are MemoryBlockEvent instances
        for event in topic_info.events:
            self.assertTrue(isinstance(event, create_schedule.MemoryBlockEvent))

    ## ------------------------End of test block---------------------
    
    def test_build_events_for_practice_topic1(self):
        # Create a mock TopicInfo instance for testing
        proportion = 1
        time_remaining = 90
        topic_info = create_schedule.TopicInfo("Test Topic", "practice", proportion, time_remaining)

        # Call the function to be tested
        create_schedule.build_events_for_memory_topic(topic_info)

        # Assert the changes made by the function
        self.assertEqual(len(topic_info.events), 2)  # Check if two events are added



if '__name__' == '__main__':
    unittest.main()