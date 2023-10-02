import unittest 
import schedule

class test_schedule(unittest.TestCase):

    def test_get_events(self):
       #dictionary type
       # events[start][dateTime]
       # events[end][dateTime]
       # events[summary]
       
       # test to see if it is getting event object
        # check if possible to simulate data called from api 
       schedule.get_events()
    #def test_extract_event_data(self):
        sample_events = {"summary" : "Study", 
                        'start' : {'dateTime' : "2022-07-03T00:00:00-07:00"}, 
                        "end" : {'dateTime': '2022-07-03T02:45:00-07:00'}}
    #def test_save_to_csv(self):