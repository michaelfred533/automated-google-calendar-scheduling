"""
test script for create_schedule.py
"""
# 3rd party imports

# python built in imports
import datetime
import unittest
from unittest import mock

# local imports
import create_schedule
from create_schedule_package import helper_functions
from create_schedule_package.event import Event, MemoryBlockEvent
from create_schedule_package.topic_info import TopicInfo 

import get_calendar_data


service = get_calendar_data.access_calendar()

#TODO: refactor code into helper functions 
class Helpers:
      
    @staticmethod
    def create_sample_standard_event(name: str, duration: int, study_type: str, start_time: str, end_time: str) -> Event:
        event = Event(name, duration, study_type)
        event.start_time = helper_functions.create_timezone_datetime_object('T' + start_time)
        event.end_time = helper_functions.create_timezone_datetime_object('T' + end_time)

        return event

    @staticmethod
    def simulate_expected_event_from_google_calendar(start_time, end_time):
        start_time = str(helper_functions.create_timezone_datetime_object('T' + start_time))
        start_time = start_time.split(' ')[0] + 'T' + start_time.split(' ')[1]

        end_time = str(helper_functions.create_timezone_datetime_object('T' + end_time))
        end_time = end_time.split(' ')[0] + 'T' + end_time.split(' ')[1]

        simulated_google_calendar_event = {
            'start' : {'dateTime' : start_time},
            'end' : {'dateTime' : end_time},
        }

        return simulated_google_calendar_event

    @staticmethod
    def interleave_assert_maximally_distributed(subject_list, result):                        
        for subject in subject_list:
            indexes = [index for index, value in enumerate(result) if value == subject] # gets all indexes for given subject
            distances_from_same_subject =[] 
            for i in range(len(indexes)-1):
                distances_from_same_subject.append(indexes[i+1] - indexes[i])
            for i in range(len(distances_from_same_subject)-1):
                assert abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]) <= 1
                print(abs(distances_from_same_subject[i+1]-distances_from_same_subject[i]))
    
    @staticmethod
    def assertEqual_created_with_expected_calendar_events(created_event, expected_event):
        assert created_event['summary'] == expected_event['summary']
        assert created_event['start']['dateTime'][11:19] == expected_event['start']['dateTime'][11:19]
        assert created_event['end']['dateTime'][11:19] == expected_event['end']['dateTime'][11:19]

    @staticmethod
    def get_created_test_events_from_todays_calendar():
        def select_only_test_events(all_events):
                created_events = []
                for event in all_events:
                    if 'test - ' in event['summary']:
                        created_events.append(event)
                
                return created_events

        calendar_events = create_schedule.get_todays_calendar()
        created_events = select_only_test_events(calendar_events)

        return created_events

    @staticmethod
    def delete_created_test_events():
         
        def delete_event(event):
            service.events().delete(calendarId = 'primary', eventId=event['id']).execute()
            
        calendar_events = create_schedule.get_todays_calendar()

        for event in calendar_events:
            if 'test - ' in event['summary']:
                delete_event(event) 

#TODO: separate into separate classes
class test_create_end_to_end(unittest.TestCase):
    """
    contains all end-to-end tests for create_schedule.py
    """
    def test_end_to_end1(self):
        """
        Tests the entire program for the case when a user enters only 1 topic type 
        """

        user_input_info = {
            'total_time' : 120,   
            'topics' : ['test - A'],
            'proportions' : [1],
            'study_type_list' : ['practice'], 
        }

        create_schedule.run_program(user_input_info)

        # tests: verify that the events were created successfully
        created_events = Helpers.get_created_test_events_from_todays_calendar()
        
        # delete test events that were just created
        Helpers.delete_created_test_events()

        expected_events = [
            {'summary': 'test - A - practice', 'start': {'dateTime' : '2023-12-02T09:00:00-08:00'}, 'end': {'dateTime' : '2023-12-02T10:30:00-08:00'}},
            {'summary': 'test - A - practice', 'start': {'dateTime' : '2023-12-02T10:30:00-08:00'}, 'end': {'dateTime' : '2023-12-02T11:00:00-08:00'}},
        ]
        
        for created_event, expected_event in zip(created_events, expected_events):
            Helpers.assertEqual_created_with_expected_calendar_events(created_event, expected_event)
            
    def test_end_to_end2(self):
        """
        Tests the entire program for the case when a user enters 2 or more topic types
        """    


        user_input_info = {
            'total_time' : 120,   
            'topics' : ['test - A', 'test - X', 'test - Y'],
            'proportions' : [.33, .33, .34],
            'study_type_list' : ['memory', 'practice', 'practice'], 
        }

        create_schedule.run_program(user_input_info)


        # tests: verify that the events were created successfully
        created_events = Helpers.get_created_test_events_from_todays_calendar()

        # delete test events that were just created
        Helpers.delete_created_test_events()

        expected_events = [
            {'summary': 'test - Y - practice', 'start': {'dateTime' : '2023-12-02T09:00:00-08:00'}, 'end': {'dateTime' : '2023-12-02T09:45:00-08:00'}},
            {'summary': 'test - A - study', 'start': {'dateTime' : '2023-12-02T09:45:00-08:00'}, 'end': {'dateTime' : '2023-12-02T10:15:00-08:00'}},
            {'summary': 'test - A - recall', 'start': {'dateTime' : '2023-12-02T10:15:00-08:00'}, 'end': {'dateTime' : '2023-12-02T10:30:00-08:00'}},
            {'summary': 'test - X - practice', 'start': {'dateTime' : '2023-12-02T10:30:00-08:00'}, 'end': {'dateTime' : '2023-12-02T11:15:00-08:00'}},
        ]

        for created_event, expected_event in zip(created_events, expected_events):
            Helpers.assertEqual_created_with_expected_calendar_events(created_event, expected_event)
            

class test_create(unittest.TestCase):
    """
    contains all unit and integration tests for create_schedule.py
    """
    ## ------------------------End of test block---------------------

    ## ------------------------End of test block---------------------

    ## ------------------------End of test block---------------------

    # artificially feeds created events to be added to google calendar
    def test_add_events_to_google_calendar_unit(self):

        # input:
        
        standard_event1 = Helpers.create_sample_standard_event('test - event 1', 60, 'sample', '09:00:00', '10:00:00')
        standard_event2 = Helpers.create_sample_standard_event('test - event 2', 60, 'sample', '11:00:00', '12:00:00')


        memory_block_event1 = MemoryBlockEvent('test - MemoryBlock event', 60, '', study_duration=45, recall_duration=15)

        memory_block_start_and_end_times = {
            'start' : helper_functions.create_timezone_datetime_object('T14:00:00'),
            'end' : helper_functions.create_timezone_datetime_object('T15:00:00'),
        }
        memory_block_event1.set_start_and_end_times(memory_block_start_and_end_times)


        input_events = [standard_event1, standard_event2, memory_block_event1]



        # output:
        create_schedule.add_events_to_google_calendar(input_events)

        # expected: 
        
        # regular events
        expected_event1 = Helpers.simulate_expected_event_from_google_calendar('09:00:00', '10:00:00')
        expected_event2 = Helpers.simulate_expected_event_from_google_calendar('11:00:00', '12:00:00')

        # memory block study and recall events
        expected_event_study = Helpers.simulate_expected_event_from_google_calendar('14:00:00', '14:45:00')
        expected_event_recall = Helpers.simulate_expected_event_from_google_calendar('14:45:00', '15:00:00')

        expected_events = [expected_event1, expected_event2, expected_event_study, expected_event_recall]

        # verify that events were created
        created_events = Helpers.get_created_test_events_from_todays_calendar()

        # cleanup events that were created during the test
        Helpers.delete_created_test_events()

        # tests:
        for created_event, expected_event in zip(created_events, expected_events):
            self.assertEqual(created_event['start']['dateTime'], expected_event['start']['dateTime'])
            self.assertEqual(created_event['end']['dateTime'], expected_event['end']['dateTime'])
            

    # tests integration with add_start_and_end_times_for_events()
    def test_add_events_to_google_calendar_integrated(self):

        # input:
        standard_event1 = Event('test - event 1', 60, 'study type')
        standard_event2 = Event('test - event 2', 60, 'study type')
        memory_block_event1 = MemoryBlockEvent('test - MemoryBlock event', 60, '', study_duration=45, recall_duration=15)

        # simulate existing google calendar event
        existing_events = [
            Helpers.simulate_expected_event_from_google_calendar('10:00:00', '11:30:00')
        ]


        # output:
        input_events = [standard_event1, standard_event2, memory_block_event1]
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            create_schedule.add_start_and_end_times_for_events(input_events)


        # output:
        create_schedule.add_events_to_google_calendar(input_events)


        # expected: 
        
        # regular events
        expected_event1 = Helpers.simulate_expected_event_from_google_calendar('09:00:00', '10:00:00')
        expected_event2 = Helpers.simulate_expected_event_from_google_calendar('11:30:00', '12:30:00')
        
        # memory block study and recall events
        expected_event_study = Helpers.simulate_expected_event_from_google_calendar('12:30:00', '13:15:00')
        expected_event_recall = Helpers.simulate_expected_event_from_google_calendar('13:15:00', '13:30:00')
        

        expected_events = [expected_event1, expected_event2, expected_event_study, expected_event_recall]

        # confirm the events were created
        created_events = Helpers.get_created_test_events_from_todays_calendar()
        
        # cleanup events that were created during the test
        Helpers.delete_created_test_events()

        # tests:
        for created_event, expected_event in zip(created_events, expected_events):
            self.assertEqual(created_event['start']['dateTime'], expected_event['start']['dateTime'])
            self.assertEqual(created_event['end']['dateTime'], expected_event['end']['dateTime'])
            
    ## ------------------------End of test block---------------------

    def test_create_google_calendar_event_parent(self):
        
        #input:         
        input_event = Helpers.create_sample_standard_event('test - single event', 60, 'sample', '09:00:00', '10:00:00')
        input_event.create_google_calendar_event()
        
        # Confirm that the event was created
        created_events = Helpers.get_created_test_events_from_todays_calendar()

        # cleanup events that were created during the test
        Helpers.delete_created_test_events()
        
        #tests: 
        self.assertTrue(created_events != None)
        self.assertTrue(created_events != [])
        self.assertTrue(created_events[0]['start']['dateTime'][:-6] == input_event.start_time)

    def test_create_google_calendar_event_child_MemoryBlock(self):
        
        #input:         
        input_event = MemoryBlockEvent('test - MemoryBlock event', 60, '', study_duration=45, recall_duration=15)

        input_start_and_end_times = {
            'start' : helper_functions.create_timezone_datetime_object('T13:00:00'),
            'end' : helper_functions.create_timezone_datetime_object('T14:00:00'),
        }
        input_event.set_start_and_end_times(input_start_and_end_times)


        input_event.create_google_calendar_event()
        
        # Confirm that the event was created
        created_events = Helpers.get_created_test_events_from_todays_calendar()

        # cleanup events that were created during the test
        Helpers.delete_created_test_events()

        #tests: 
        self.assertTrue(created_events != [])
        
        self.assertTrue(created_events[0]['start']['dateTime'][:-6] == input_event.study_event.start_time)
        self.assertTrue(created_events[0]['end']['dateTime'][:-6] == input_event.study_event.end_time)

        self.assertTrue(created_events[1]['start']['dateTime'][:-6] == input_event.recall_event.start_time)
        self.assertTrue(created_events[1]['end']['dateTime'][:-6] == input_event.recall_event.end_time)


    ## ------------------------End of test block---------------------


    # 1 and 2 use mock.patch to mock get_todays_calendar
    def test_add_start_and_end_times_for_events1(self):
        # input:
        event1 = Helpers.simulate_expected_event_from_google_calendar('10:00:00', '11:30:00')
        event2 = Helpers.simulate_expected_event_from_google_calendar('11:30:00', '12:30:00')
        existing_events = [event1, event2]
        

        result = [Event('test - A', 60, 'practice'), Event('test - B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            create_schedule.add_start_and_end_times_for_events(result)
        print('mock shedule: ', result)
        # expected: 
        event1 = Helpers.create_sample_standard_event('test - A', 60, 'practice', '09:00:00', '10:00:00')
        event2 = Helpers.create_sample_standard_event('test - B', 60, 'practice', '12:30:00', '13:30:00')

        expected = [event1, event2]

        # tests: 
        # check that each attribute matches for each event in the schedule
        for event_expected, event_result in zip(expected, result):
            self.assertEqual(event_expected, event_result) # uses dataclass functionality to directly compare events

    def test_add_start_and_end_times_for_events2(self):
        # input:
        existing_event1 = Helpers.simulate_expected_event_from_google_calendar('09:00:00', '10:30:00')
        existing_event2 = Helpers.simulate_expected_event_from_google_calendar('11:30:00', '12:00:00')
        existing_events = [existing_event1, existing_event2]
        
        
        result = [Event('test - A', 60, 'practice'), Event('test - B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            create_schedule.add_start_and_end_times_for_events(result)
        print('mock shedule: ', result)

        # expected: 
        expected_event1 = Helpers.create_sample_standard_event('test - A', 60, 'practice', '10:30:00', '11:30:00')
        expected_event2 = Helpers.create_sample_standard_event('test - B', 60, 'practice', '12:00:00', '13:00:00')

        expected = [expected_event1, expected_event2]
        
        # tests: 
        # check that each attribute matches for each event in the schedule
        for event_expected, event_result in zip(expected, result):
            self.assertEqual(event_expected, event_result)

    # 3 adds actual test event to the calendar
    def test_add_start_and_end_times_for_events3(self):
         # add events that the function must schedule around to google calendar:
        event_to_add = Helpers.create_sample_standard_event('test - A' , 60, 'practice', '09:00:00', '10:00:00')
        event_to_add.create_google_calendar_event()
       
        # input:
        result = [Event('test - A', 60, 'practice'), Event('test - B', 60, 'practice')]

        # output:
        create_schedule.add_start_and_end_times_for_events(result)

        # delete test events created for this test
        Helpers.delete_created_test_events()

    
        # expected
        event1 = Helpers.create_sample_standard_event('test - A', 60, 'practice', '09:00:00', '10:00:00')
        event2 = Helpers.create_sample_standard_event('test - B', 60, 'practice', '11:00:00', '12:00:00')

        expected = [event1, event2]

        # tests: 
        for event_expected, event_result in zip(expected, result):
            self.assertEqual(event_expected, event_result)

    #----------------------End of test block---------------------
    
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
        Helpers.interleave_assert_maximally_distributed(subject_list, result)
        

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
        Helpers.interleave_assert_maximally_distributed(subject_list, result)

    ## ------------------------End of test block---------------------

    #----------------------End of test block---------------------
    def test_build_events_for_memory_topic1(self):
        # Create a mock TopicInfo instance for testing
        topic_info = TopicInfo("Test Topic", "study", 1, 60)

        # Call the function to be tested
        create_schedule.build_events_for_memory_topic(topic_info)

        # Assert the changes made by the function
        print(topic_info.events)
        self.assertEqual(len(topic_info.events), 1)  # Check if two events are added

        # Assert that the added events are MemoryBlockEvent instances
        for event in topic_info.events:
            self.assertTrue(isinstance(event, MemoryBlockEvent))

    def test_build_events_for_memory_topic2(self):
        # Create a mock TopicInfo instance for testing
        proportion = 1
        time_remaining = 90
        topic_info = TopicInfo("Test Topic", "study", proportion, time_remaining)

        # Call the function to be tested
        create_schedule.build_events_for_memory_topic(topic_info)

        # Assert the changes made by the function
        self.assertEqual(len(topic_info.events), 2)  # Check if two events are added

        # Assert that the added events are MemoryBlockEvent instances
        for event in topic_info.events:
            self.assertTrue(isinstance(event, MemoryBlockEvent))

    ## ------------------------End of test block---------------------
    
    def test_build_events_for_practice_topic1(self):
        # Create a mock TopicInfo instance for testing
        proportion = 1
        time_remaining = 90
        topic_info = TopicInfo("Test Topic", "practice", proportion, time_remaining)

        # Call the function to be tested
        create_schedule.build_events_for_memory_topic(topic_info)

        # Assert the changes made by the function
        self.assertEqual(len(topic_info.events), 2)  # Check if two events are added



if '__name__' == '__main__':
    unittest.main()