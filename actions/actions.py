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

class ValidateUserInfoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fetch_user_info_form"
    
    async def required_slots(self,domain_slots: List[Text],dispatcher: "CollectingDispatcher",tracker: "Tracker",domain: "DomainDict") -> List[Text]:
        if tracker.slots.get("date") != None and tracker.slots.get("time") == None and tracker.slots.get('email_id') == None:
            return ['date', 'time', 'email_id']
        return domain_slots

    def time_validation_helper(self, date_entity):
        pattern = re.compile("(([01]?[0-9]):([0-5][0-9]) ([AaPp][Mm]))")
        return pattern.match(date_entity)

    def date_validation_helper(self, date_entity):
        valid_date = None
        now = datetime.now()
        for possible_date in datefinder.find_dates(date_entity):
            valid_date = possible_date if possible_date > now else None
        return valid_date

    async def extract_date(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if tracker.slots.get("date") != None:
            return tracker.slots.get("date")
        entities = tracker.latest_message['entities']
        extracted_date = {"date": None}
        if entities != None and len(entities) >= 1:
            for entity in entities:
                if entity["entity"] == "date":
                    extracted_date["date"] = entity["value"]
        return extracted_date

    async def extract_time(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if tracker.slots.get("time") != None:
            return tracker.slots.get("time")
        entities = tracker.latest_message['entities']
        extracted_time = {"time": None}
        if entities != None and len(entities) >= 1:
            for entity in entities:
                if entity["entity"] == "time":
                    extracted_time["time"] = entity["value"]
        return extracted_time

    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value == None:
            return {"date": None}
        if self.date_validation_helper(slot_value) == None:
            dispatcher.utter_message(text=f"The date you have provided is invalid")
            return {"date": None}
        dispatcher.utter_message(text=f"OK! Your date is {slot_value}. Please provide the time for the connect next.")
        return {"date": slot_value}

    def validate_time(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,) -> Dict[Text, Any]:
        if slot_value is None:
            return {"time": None}
        if self.time_validation_helper(slot_value) == None:
            dispatcher.utter_message(text=f"The time is invalid.")
            return {"time": None}
        dispatcher.utter_message(text=f"Your Time slot is {slot_value}.")
        return {"time": slot_value}
    
    def is_email_valid_domain(self,email):
        addr = email.split('@')[1]
        return addr in constants["valid_domains"]

    def email_validation_helper(self,email):
        return self.is_email_valid_domain(email)
    
    def validate_email_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if self.email_validation_helper(slot_value) == False:
            dispatcher.utter_message(text=f"The email is invalid")
            return {"email_id": None}
        dispatcher.utter_message(text=f"Your email is {slot_value}.")
        return {"email_id": slot_value}