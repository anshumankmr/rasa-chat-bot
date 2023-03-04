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
        print(date_entity,datefinder.find_dates(date_entity))
        valid_date = None
        now = datetime.now()
        for possible_date in datefinder.find_dates(date_entity):#find possible dates in a
            valid_date = possible_date if possible_date > now else None
        return valid_date

    def get_selected_entity(self,tracker,entity_name):
        entities = tracker.latest_message['entities']
        extracted_entity = {f"{entity_name}": None}
        if entities != None and len(entities) >= 1:
            for entity in entities:
                if entity["entity"] == entity_name:
                    extracted_entity[entity_name] = entity["value"]
        return extracted_entity

    async def extract_date(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if tracker.slots.get("date") != None:
            return tracker.slots.get("date")
        return self.get_selected_entity(tracker = tracker,entity_name="date")
        
    async def extract_time(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if tracker.slots.get("time") != None:
            return tracker.slots.get("time")
        return self.get_selected_entity(tracker = tracker,entity_name="time")

    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print(tracker.latest_message['entities'])
        time_entity = self.get_selected_entity(tracker=tracker,entity_name="time")
        if slot_value == None:
            return {"date": None}
        if self.date_validation_helper(slot_value) == None:
            if time_entity is None:
                dispatcher.utter_message(text=f"The date you have provided is invalid")
            else:
                dispatcher.utter_message(text=f"The date you have provided is invalid and")
            return {"date": None}
        if not time_entity:
            dispatcher.utter_message(text=f"OK! The date you have provided is {slot_value}. Please provide the time for the connect next.")
        else:
            dispatcher.utter_message(text=f"OK! The date you have provided {slot_value} and")
        return {"date": slot_value}

    def validate_time(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,) -> Dict[Text, Any]:
        if slot_value is None:
            return {"time": None}
        date_entity = self.get_selected_entity(tracker=tracker,entity_name="date")
        if self.time_validation_helper(slot_value) == None:
            if date_entity is not None:
                dispatcher.utter_message(text=f"the time you have provided is invalid.")
            else:
                dispatcher.utter_message(text=f"The time you have provided is invalid.")
            return {"time": None}
        if not date_entity:
            dispatcher.utter_message(text=f"Your time slot is {slot_value}.")
        else:
            dispatcher.utter_message(text=f"and the time you have provided is {slot_value}")
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