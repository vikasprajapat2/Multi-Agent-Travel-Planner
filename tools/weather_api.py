import os 
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# season data per destination
 
_WEATHER: dict[str, dict] = {
    "goa": {
        "winter": {"temp": "22-30°C", "condition": "Sunny & dry",   "advice": "Peak season — book hotels 4–6 weeks early"},
        "summer": {"temp": "28–38°C", "condition": "Hot & humid",   "advice": "Off-season, fewer crowds, 30–40% cheaper hotels"},
        "monsoon":{"temp": "24–30°C", "condition": "Heavy monsoon", "advice": "Beaches close; great for Dudhsagar waterfall hikes"},
    },
    "manali": {
        "winter": {"temp": "-10–5°C", "condition": "Heavy snowfall","advice": "Rohtang Pass closed; great for snow activities"},
        "summer": {"temp": "10–25°C", "condition": "Pleasant",      "advice": "Best time — Rohtang Pass open, all treks accessible"},
        "monsoon":{"temp": "10–20°C", "condition": "Light rain",    "advice": "Landslide risk on mountain roads; check advisories"},
    },
    "kerala": {
        "winter": {"temp": "20–32°C", "condition": "Warm & pleasant","advice": "Ideal — backwaters, beaches and wildlife at best"},
        "summer": {"temp": "28–38°C", "condition": "Hot & humid",   "advice": "Hills (Munnar, Wayanad) are cooler alternatives"},
        "monsoon":{"temp": "22–30°C", "condition": "Lush rains",    "advice": "Off-season; excellent for Ayurveda retreats"},
    },
    "jaipur": {
        "winter": {"temp": "8–25°C",  "condition": "Cool & sunny",  "advice": "Best time to visit — pleasant days, cold nights"},
        "summer": {"temp": "30–45°C", "condition": "Scorching hot", "advice": "Sightseeing only in early morning (6–10am)"},
        "monsoon":{"temp": "25–35°C", "condition": "Warm with showers","advice": "Forts and palaces look stunning in the rain"},
    },
    "delhi": {
        "winter": {"temp": "5–20°C",  "condition": "Cool, foggy mornings","advice": "Fog delays possible — buffer extra time for flights"},
        "summer": {"temp": "35–48°C", "condition": "Very hot",      "advice": "Stay indoors 11am–4pm; carry water everywhere"},
        "monsoon":{"temp": "25–38°C", "condition": "Humid with rain","advice": "Waterlogging common; use metro over road transport"},
    },
    "mumbai": {
        "winter": {"temp": "15–30°C", "condition": "Pleasant",      "advice": "Best time — cool evenings, sea breeze"},
        "summer": {"temp": "28–38°C", "condition": "Hot & humid",   "advice": "Coastal wind helps; beach evenings are pleasant"},
        "monsoon":{"temp": "24–32°C", "condition": "Heavy rains",   "advice": "Street food season! Watch for waterlogged roads"},
    },
    "maldives": {
        "winter": {"temp": "27–30°C", "condition": "Sunny & calm",  "advice": "Perfect — best visibility for snorkelling/diving"},
        "summer": {"temp": "28–32°C", "condition": "Mostly sunny",  "advice": "Good value — 20–30% lower rates than peak season"},
        "monsoon":{"temp": "26–31°C", "condition": "Occasional rain","advice": "Short showers, still beautiful — big price drops"},
    },
    "bangkok": {
        "winter": {"temp": "20–32°C", "condition": "Sunny & dry",   "advice": "Peak season — best weather but crowded and pricey"},
        "summer": {"temp": "28–38°C", "condition": "Hot",           "advice": "Very hot; temples in early morning, malls midday"},
        "monsoon":{"temp": "25–34°C", "condition": "Daily showers", "advice": "Short afternoon showers — still great for food & culture"},
    },
    "dubai": {
        "winter": {"temp": "16–26°C", "condition": "Perfect",       "advice": "Best time — outdoor activities, desert safaris"},
        "summer": {"temp": "35–47°C", "condition": "Extreme heat",  "advice": "Stay in malls and hotels — outdoor heat is dangerous"},
        "monsoon":{"temp": "28–40°C", "condition": "Hot & clear",   "advice": "Dubai has no real monsoon; summer rules still apply"},
    },
    # Generic fallback for unlisted destinations
    "default": {
        "winter": {"temp": "15–28°C", "condition": "Pleasant",      "advice": "Generally a good time to visit"},
        "summer": {"temp": "30–42°C", "condition": "Hot",           "advice": "Stay hydrated; early morning sightseeing recommended"},
        "monsoon":{"temp": "22–32°C", "condition": "Rainy",         "advice": "Carry rain gear; check local flood advisories"},
    },
}