### Google Calendar Automatic Scheduler 

This project allows the user to input different subjects to study along the time they have to study, and automatically creates an optimized learning schedule using the scientific principles of learning and memory such as interleaving and spaced practice. The program then automatically adds study sessions to the user's Google calendar and schedules around any existing events on Google calendar. 

### Learnings
- I used this project to practice the S.O.L.I.D. principles of programming

- I used this project to practice building comprehensive testing suites for my code


1. Install dependencies:
```
pip install -r requirements.txt
```
2. Enable Google Calendar API and download `credentials.json`. You can refer to [this](https://developers.google.com/workspace/guides/create-project).

* The Google Calendar access token periodically expires. To fix this, you can manually delete `token.json` from the folder and restart the script.
