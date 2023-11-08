import datetime
from datetime import time

date = datetime.datetime.today().date()
time = datetime.datetime.today().time()

full_str = str(date) + 'T09:00:00-07:00'
full_time = datetime.datetime.strptime(full_str, '%Y-%m-%dT%H:%M:%S%z')

print(full_str)
print(full_time)