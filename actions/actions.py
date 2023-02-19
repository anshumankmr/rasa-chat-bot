# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionAskForConnectionTime(Action):

    def name(self) -> Text:
        return "action_ask_for_connection_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        date = None
        for e in tracker.latest_message['entities']:
            if e["entity"] == 'date':
                date = e["value"]
        print(date)
        if date is not None: 
            dispatcher.utter_message(template="utter_ask_for_time",date=date)
        return [SlotSet("date",date)]

class ActionAskForEmail(Action):

    def name(self) -> Text:
        return "action_ask_for_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        found_ents = [e for e in tracker.latest_message['entities']]
        time = None
        for e in tracker.latest_message['entities']:
            if e["entity"] == 'time':
                time = e["value"]
        if time is not None:
            dispatcher.utter_message(template="utter_ask_for_email", time = time)
        return [SlotSet("time", time)]
