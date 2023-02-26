# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import datefinder
from datetime import datetime
from bson import json_util
from json import dumps
import re
from .config.constants import constants

class ActionAskDate(Action):

    def name(self) -> Text:
        return "action_ask_date"
    
    def valid_date(self, date_entity):
        valid_date = None
        now = datetime.now()
        for possible_date in datefinder.find_dates(date_entity):
            valid_date = possible_date if possible_date > now else None
        return valid_date

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        date = None
        for e in tracker.latest_message['entities']:
            if e["entity"] == 'date':
                date = e["value"]
        print(date,tracker.latest_message['entities'])
        if date is not None:
            valid_date = self.valid_date(date)
            print('Valid Date' , valid_date)
            if valid_date is not None: 
                dispatcher.utter_message(template="utter_ask_for_time",date=date)
            return [SlotSet("date",dumps(date,default=json_util.default))]
        # dispatcher.utter_message(template="utter_invalid_date")   
        return []


class ActionAskTime(Action):

    def name(self) -> Text:
        return "action_ask_time"
    
    def valid_time(self, date_entity):
        pattern = re.compile("(([01]?[0-9]):([0-5][0-9]) ([AaPp][Mm]))")
        return pattern.match(date_entity)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        time = None
        for e in tracker.latest_message['entities']:
            if e["entity"] == 'time':
                time = e["value"]
        if time is not None:
            valid_time = self.valid_time(time)
            print(valid_time)
            if valid_time: 
                dispatcher.utter_message(template="utter_ask_for_time",date=time)
            return [SlotSet("time",time)]
        return []

class ActionAskForEmail(Action):

    def name(self) -> Text:
        return "action_ask_for_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []

class ValidateUserInfoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fetch_user_info_form"

    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("Slot Date",slot_value)
        if slot_value == None:
            dispatcher.utter_message(text=f"The date you have provided is invalid")
            return {"date": None}
        dispatcher.utter_message(text=f"OK! Your date is {slot_value}.")
        return {"date": slot_value}

    def validate_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print('Validate Time', slot_value)
        if not slot_value:
            dispatcher.utter_message(text=f"The time is invalid")
            return {"time": None}
        dispatcher.utter_message(text=f"Your Time slot is {slot_value} .")
        return {"time": slot_value}
    
    def is_email_valid_domain(self,email):
        print(email)
        addr = email.split('@')[1]
        print(addr, addr in constants["valid_domains"])
        return addr in constants["valid_domains"]

    def validate_email_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print(slot_value)
        if self.is_email_valid_domain(slot_value) == False:
            dispatcher.utter_message(text=f"The email is invalid")
            return {"email_id": None}
        dispatcher.utter_message(text=f"Your email is  {slot_value} .")
        return {"email_id": slot_value}