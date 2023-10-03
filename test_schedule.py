import unittest 
import schedule

class test_schedule(unittest.TestCase):

    def test_get_events(self):

        
        # input:
        start_date = "2023-10-02"
        end_date = "2023-10-04"

        # output:
        result = schedule.get_events(start_date, end_date)

        # expected:
        expected = [{
                "status" : "confirmed",
                "summary" : "Test Case",
                "creator" : {"email" : "michaelfred@live.com", "self" : True},
                "organizer" : {"email" : "michaelfred@live.com", "self" : True},
                "start" : {"dateTime" : "2023-10-02T13:00:00-07:00", "timeZone" : "America/Los_Angeles"},
                "end" : {"dateTime" : "2023-10-02T14:00:00-07:00", "timeZone" : "America/Los_Angeles"},
                }, 
                {"status" : "confirmed",
                "summary" : "Test cas",
                "creator" : {"email" : "michaelfred@live.com", "self" : True},
                "organizer" : {"email" : "michaelfred@live.com", "self" : True},
                "start" : {"dateTime" : "2023-10-03T14:00:00-07:00", "timeZone" : "America/Los_Angeles"},
                "end" : {"dateTime" : "2023-10-03T14:30:00-07:00", "timeZone" : "America/Los_Angeles"},
                }
                ]

        # tests:
        self.assertEqual(len(result), 2)

        # event 1
        self.assertEqual(result[0]['status'], expected[0]['status'])
        self.assertEqual(result[0]['summary'], expected[0]['summary'])
        self.assertEqual(result[0]['creator'], expected[0]['creator'])
        self.assertEqual(result[0]['organizer'], expected[0]['organizer'])
        self.assertEqual(result[0]['start'], expected[0]['start'])
        self.assertEqual(result[0]['end'], expected[0]['end'])

        # event 2
        self.assertEqual(result[1]['status'], expected[1]['status'])
        self.assertEqual(result[1]['summary'], expected[1]['summary'])
        self.assertEqual(result[1]['creator'], expected[1]['creator'])
        self.assertEqual(result[1]['organizer'], expected[1]['organizer'])
        self.assertEqual(result[1]['start'], expected[1]['start'])
        self.assertEqual(result[1]['end'], expected[1]['end'])


    def test_extract_event_data(self):
        
        # input:
        input = [{
                "status" : "confirmed",
                "summary" : "Test Case",
                "creator" : {"email" : "michaelfred@live.com", "self" : True},
                "organizer" : {"email" : "michaelfred@live.com", "self" : True},
                "start" : {"dateTime" : "2023-10-02T13:00:00-07:00", "timeZone" : "America/Los_Angeles"},
                "end" : {"dateTime" : "2023-10-02T14:00:00-07:00", "timeZone" : "America/Los_Angeles"},
                }, 
                {"status" : "confirmed",
                "summary" : "Test cas",
                "creator" : {"email" : "michaelfred@live.com", "self" : True},
                "organizer" : {"email" : "michaelfred@live.com", "self" : True},
                "start" : {"dateTime" : "2023-10-03T14:00:00-07:00", "timeZone" : "America/Los_Angeles"},
                "end" : {"dateTime" : "2023-10-03T14:30:00-07:00", "timeZone" : "America/Los_Angeles"},
                }
                ]
    
        # output:
        result_all_days, result_total = schedule.extract_event_data(input)

        # expected:
        expected_all_days = {'2023-10-02' : {'test case' : 60.0}, '2023-10-03' : {'test case' : 30.0}}
        expected_total = {'test case' : 90.0}
    
        # tests:
        print(type(result_all_days), type(result_total))
        print(len(result_all_days), len(result_total))
        self.assertEqual(result_all_days, expected_all_days)
        self.assertEqual(result_total, expected_total)


    def test_save_to_csv(self):
        # input:

        # output:

        # expected:

        # tests: 
