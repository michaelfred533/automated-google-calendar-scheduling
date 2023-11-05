"""
test the function of create_schedule.py
"""

import unittest
from unittest import mock
import create_schedule
import schedule

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

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

    def test_get_todays_calendar(self):

        start_date = "2023-10-04"
        end_date = "2023-10-06" 

        service = schedule.access_calendar(SCOPES)
        events = schedule.get_events(service, start_date, end_date)

        print(events)
        
    ## ------------------------End of test block---------------------

    def test_schedule_events(self):
        # input:
        existing_events = [{'start' : {'dateTime' : '2023-10-05T10:00:00-07:00'}, 'end' : {'dateTime' : '2023-10-05T11:00:00-07:00'}}]
        new_events = [create_schedule.Event('A', 60, 'practice'), create_schedule.Event('B', 60, 'practice')]

        # output:
        with mock.patch('create_schedule.get_todays_calendar', return_value = existing_events):
            schedule = create_schedule.schedule_events(new_events, existing_events)
        print('mock shedule: ', schedule)
        # expected: 
        event1 = create_schedule.Event('A', 60, 'practice')
        event2 = create_schedule.Event('B', 60, 'practice')
        expected = [event1, event2]
        for event in expected:
            event['duration'] = event['end_time'] - event['start_time']
        expected = [
                    {'name': 'A', 'start_time' : '2023-10-05T09:00:00-07:00', 'end_time' : '2023-10-05T10:00:00-07:00'}, 
                    {'name' : 'B', 'start_time' : '2023-10-05T11:00:00-07:00', 'end_time' : '2023-10-05T12:00:00-07:00'}
                    ]

        # tests: 
        #self.assertEqual(expected, schedule)

    ## ------------------------End of test block---------------------


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