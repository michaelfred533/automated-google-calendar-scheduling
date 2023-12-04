"""
contains topic_info class
"""
# built-in python imports
from dataclasses import dataclass, field


@dataclass
class TopicInfo:
    topic: str
    study_type: str
    proportion: float
    time_remaining: int
    events: list = field(default_factory=list) # No defualt mutable arguments allowed, use default_factory instead

    def __str__(self):
        event_list = "\n".join([str(event) for event in self.events])
        return f"Topic: {self.topic}, Study Type: {self.study_type}, Proportion: {self.proportion}, Time Remaining: {self.time_remaining}\nEvents:\n\t{event_list}"

