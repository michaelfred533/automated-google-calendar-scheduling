"""
test the function of create_schedule.py
"""
import datetime
from datetime import time

import unittest
from unittest import mock
import create_schedule
import schedule

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

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

    #TODO: refactor code into helper functions 
    def helper_create_sample_events(self):
        date = str(datetime.date.today())
        existing_events = [
            {'start' : {'dateTime' : date + 'T10:00:00-07:00'}, 'end' : {'dateTime' : date + 'T11:30:00-07:00'}},
            {'start' : {'dateTime' : date + 'T11:30:00-07:00'}, 'end' : {'dateTime' : date + 'T12:30:00-07:00'}},
            ]

    def test_schedule_events1(self):
        # input:

        date = str(datetime.date.today())
        existing_events = [
            {'start' : {'dateTime' : date + 'T10:00:00-07:00'}, 'end' : {'dateTime' : date + 'T11:30:00-07:00'}},
            {'start' : {'dateTime' : date + 'T11:30:00-07:00'}, 'end' : {'dateTime' : date + 'T12:30:00-07:00'}},
            ]
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            result = create_schedule.schedule_events(new_events)
        print('mock shedule: ', schedule)
        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        event1.start_time, event1.end_time = datetime.datetime.strptime(date + 'T09:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z'), datetime.datetime.strptime(date + 'T10:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z') 
        event2.start_time, event2.end_time = datetime.datetime.strptime(date + 'T12:30:00-07:00', '%Y-%m-%dT%H:%M:%S%z'), datetime.datetime.strptime(date + 'T13:30:00-07:00', '%Y-%m-%dT%H:%M:%S%z')

        expected = [event1, event2]

        # tests: 
        # check that each attribute matches for each event in the schedule
        for event_expected, event_result in zip(expected, result):
            attributes_expected = [attr for attr in dir(event_expected) if not callable(getattr(event_expected, attr)) and not attr.startswith("__")]
            attributes_result = [attr for attr in dir(event_result) if not callable(getattr(event_result, attr))and not attr.startswith("__")]
            for attr_name in attributes_expected:
                attr_expected = getattr(event_expected, attr_name)
                attr_result = getattr(event_result, attr_name)
                self.assertEqual(attr_expected, attr_result)

    def test_schedule_events2(self):
        # input:

        date = str(datetime.date.today())
        existing_events = [
            {'start' : {'dateTime' : date + 'T09:00:00-07:00'}, 'end' : {'dateTime' : date + 'T10:30:00-07:00'}},
            {'start' : {'dateTime' : date + 'T11:30:00-07:00'}, 'end' : {'dateTime' : date + 'T12:00:00-07:00'}},
            ]
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            result = create_schedule.schedule_events(new_events)
        print('mock shedule: ', schedule)

        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        event1.start_time, event1.end_time = datetime.datetime.strptime(date + 'T10:30:00-07:00', '%Y-%m-%dT%H:%M:%S%z'), datetime.datetime.strptime(date + 'T11:30:00-07:00', '%Y-%m-%dT%H:%M:%S%z') 
        event2.start_time, event2.end_time = datetime.datetime.strptime(date + 'T12:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z'), datetime.datetime.strptime(date + 'T13:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z')

        expected = [event1, event2]
        
        # tests: 
        # check that each attribute matches for each event in the schedule
        for event_expected, event_result in zip(expected, result):
            attributes_expected = [attr for attr in dir(event_expected) if not callable(getattr(event_expected, attr)) and not attr.startswith("__")]
            attributes_result = [attr for attr in dir(event_result) if not callable(getattr(event_result, attr))and not attr.startswith("__")]
            for attr_name in attributes_expected:
                attr_expected = getattr(event_expected, attr_name)
                attr_result = getattr(event_result, attr_name)
                print(attr_expected)
                print(attr_result)
                self.assertEqual(attr_expected, attr_result)

    def test_get_todays_calendar(self):

        start_date = "2023-10-04"
        end_date = "2023-10-06" 

        service = schedule.access_calendar(SCOPES)
        events = schedule.get_events(service, start_date, end_date)

        #print(events)
        #events[0]['start']['dateTime']
        print(type(events[0]['start']['dateTime']))
    
    #TODO: finish this  
        #TODO: use function that adds an event to the calendar at X time on current date
    def test_schedule_events3(self):
        # input:
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        result = create_schedule.schedule_events(new_events)

        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        
        date = str(datetime.date.today())
        event1.start_time, event1.end_time = datetime.datetime.strptime(date + '10:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z'), datetime.datetime.strptime(date + '11:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z') 
        event2.start_time, event2.end_time = datetime.datetime.strptime(date + '12:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z'), datetime.datetime.strptime(date + '13:00:00-07:00', '%Y-%m-%dT%H:%M:%S%z')

        expected = [event1, event2]
        
        #for event

        # tests: 
        # for event_expected, event_result in zip(expected, result):
        #     attributes_expected = [attr for attr in dir(event_expected) if not callable(getattr(event_expected, attr)) and not attr.startswith("__")]
        #     attributes_result = [attr for attr in dir(event_result) if not callable(getattr(event_result, attr))and not attr.startswith("__")]
        #     for attr_name in attributes_expected:
        #         attr_expected = getattr(event_expected, attr_name)
        #         attr_result = getattr(event_result, attr_name)
        #         print(attr_expected)
        #         print(attr_result)
        #         self.assertEqual(attr_expected, attr_result)

    #----------------------End of test block---------------------
    
    def test_create_google_calendar_event(self):
        
        #input:         
        input_event = create_schedule.Event('A', 60, 'practice')

        date = str(datetime.date.today())
        input_event.start_time = date + 'T09:00:00'
        input_event.end_time = date + 'T10:00:00'

        #result:
        result = create_schedule.create_google_calendar_event(input_event)
        
        #expected:
        
        #tests: 
        #TODO: use other function to get calendar to confirm that the event is created
        
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
            differences =[]
            for i in range(len(indexes)-1):
                differences.append(indexes[i+1] - indexes[i])
            for i in range(len(differences)-1):
                self.assertTrue(abs(differences[i+1]-differences[i]) <= 1)
                print(abs(differences[i+1]-differences[i]))
        
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
        # makes sure that each element is maximally distributed 
        for subject in subject_list:
            indexes = [index for index, value in enumerate(result) if value == subject]
            differences =[]
            for i in range(len(indexes)-1):
                differences.append(indexes[i+1] - indexes[i])
            for i in range(len(differences)-1):
                self.assertTrue(abs(differences[i+1]-differences[i]) <= 1)
                print(abs(differences[i+1]-differences[i]))
        
    ## ------------------------End of test block---------------------

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