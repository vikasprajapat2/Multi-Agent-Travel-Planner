import os
import sys
import random
import requests
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()
 
from config import USE_MOCK_APIS
 
RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY",  "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "booking-com15.p.rapidapi.com")


# Data classes

@dataclass
class TrainOption:
    train_name:    str
    train_number:  str
    origin:        str
    destination:   str
    depart_time:   str
    arrive_time:   str
    duration:      str
    distance_km:   int
    travel_class:  str    # SL | 3A | 2A | 1A
    price_inr:     int    # total for all passengers
    availability:  str    # "Available" | "Waitlist" | "RAC"
    days_of_run:   str    # "Daily" | "Mon,Wed,Fri" etc.

    def to_dict(self) -> dict:
        return asdict(self)
 
    def summary(self) -> str:
        return (
            f"{self.train_name} ({self.train_number}) | "
            f"{self.depart_time} → {self.arrive_time} ({self.duration}) | "
            f"{self.travel_class} | Rs.{self.price_inr:,}"
        )

@dataclass
class BusOption:
    operator:      str
    bus_type:      str    # Sleeper | AC Sleeper | Volvo AC | Non-AC Seater
    origin:        str
    destination:   str
    depart_time:   str
    arrive_time:   str
    duration:      str
    price_inr:     int    # total for all passengers
    seats_left:    int
    amenities:     list   # ["USB Charging", "Blanket", "Water bottle"]
    rating:        float  # out of 5
 
    def to_dict(self) -> dict:
        return asdict(self)
 
    def summary(self) -> str:
        return (
            f"{self.operator} | {self.bus_type} | "
            f"{self.depart_time} → {self.arrive_time} ({self.duration}) | "
            f"Rs.{self.price_inr:,} | {self.seats_left} seats left"
        )