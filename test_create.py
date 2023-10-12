"""
test the function of create_schedule.py
"""

import unittest
import create_schedule

class test_create(unittest.TestCase):

    def test_mix_lists(self):

        # input:
        events_1, events_2 = ['A', 'B'], ['W', 'X', 'Y', 'Z']
        
        # result:
        result = create_schedule.mix_lists(events_1, events_2)

        # expected:
        expected = ['W', 'A', 'X', 'B', 'Y', 'Z']

        # tests:
        self.assertEqual(result, expected)
        self.assertEqual(len(result), (len(events_1) + len(events_2)))
        

    def test_mix_lists2(self):

        # input:
        events_1, events_2 = ['A', 'B'], ['W', 'X', 'Y']
        
        # result:
        result = create_schedule.mix_lists(events_1, events_2)

        # expected:
        expected = ['W', 'A', 'X', 'B', 'Y']

        # tests:
        self.assertEqual(result, expected)
        self.assertEqual(len(result), (len(events_1) + len(events_2)))    

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
        # ask GPT how to sum
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
        # ask GPT how to sum
        self.assertEqual(result, expected)


    def test_interleaveX(self):
        # input:
        len_1, len_2, len_3, len_4 = 1, 2, 3, 4
        events_1 = ['A'] * len_1
        events_2 = ['B'] * len_2
        events_3 = ['Y'] * len_3
        events_4 = ['Z'] * len_4
        events = [events_1, events_2, events_3, events_4]

        # result:
        result = create_schedule.interleave(events)
        # expected: 


        # tests:
        #check for matching lengths of inputs and outputs 
        #

        pass


    ## ------------------------End of test block---------------------



if '__name__' == '__main__':
    unittest.main()