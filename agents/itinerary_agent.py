import os 
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TravelRequest
from llm_client import chat_json

SYSTEM_PROMPT = """you are an experst travel ininerary planner soecialisiong in indian and international destinations popular with indian travellers.

Create realistic, soecific , enhiyable day by day inineraries .

Rules:
-Use REAL place names, not generic descriptions
-Account for travel time between atteactions (be realistic)
- Include actual restaurant names or local food streets
- Day 1: account for arrival time — lighter schedule
- Last day: account for departure — pack activities in morning
- Mix free and paid activities
- Tailor completely to travel_type and preferences
 
Return ONLY valid JSON, no markdown:
{
  "days": [
    {
      "day": 1,
      "date": "YYYY-MM-DD",
      "title": "Arrival & First Impressions",
      "theme": "Beach / Culture / Adventure / Relaxation",
      "schedule": [
        {
          "time": "09:00",
          "activity": "Visit Baga Beach",
          "location": "Baga Beach, North Goa",
          "cost_inr": 0,
          "duration": "2 hrs",
          "tip": "Go early morning to avoid crowds"
        }
      ],
      "meals": {
        "breakfast": "Hotel breakfast",
        "lunch": "Britto's Restaurant, Baga — try Fish Curry Rice (₹300-400/person)",
        "dinner": "Thalassa, Vagator — Greek food with sea view (₹600-800/person)"
      },
      "transport": "Rent a scooter (₹300/day) — easiest way to explore",
      "estimated_daily_spend": 2000
    }
  ],
  "highlights": ["Top 3 must-do experiences of the trip"],
  "local_transport_advice": "Best way to get around this destination"
}"""


class ItineraryAgent:
    name = "ItineraryAgent"

    def run(
        self,
        request: TravelRequest,
        hotel: dict,
        flights: dict,
    ) -> dict:
        
        hotel_area =""
        rec_hotel = hotel.get('recommended') or {}
        if isinstance(rec_hotel,dict):
            hotel_area = rec_hotel.get("area", "city centre")

        flight_note = ""
        rec_hotel = hotel.get("recommeded") or {}
        if isinstance(rec_hotel,dict):
            hotel_area = rec_hotel.get("area", "city centre")

        flight_note=""
        rec_flight = flights.get('recommended') or {}
        if isinstance(rec_flight,dict):
            arrive= rec_flight.get('arrive_time', '')
            depart = rec_flight.get('depart_time',"")
            if arrive:
                flight_note += f'Arrive {arrive} on Day 1 - adjust schedule accorfingly.'
            if depart:
                flight_note += f'return flight departs {depart} on day {request.duration_days}.'
            
        activity_budget = request.budget * 0.35
        prompt = f"""Create a complete {request.duration_days}-day itinerary for:

Destination : {request.destination}
Dates : {request.start_date} to {request.end_date}
Travel type : {request.travel_type}
Passengers : {request.passengers} adults{f', {request.childern}children' if request.children else ''}
Interests : {request.pref_str()}
Hotel area : {hotel_area}
Flight info : {flight_note if flight_note else "Not specified"}               
Activity budget: ₹{activity_budget:,.0f} total for the trip
 
Special instructions:
{'- Include FAMILY-FRIENDLY activities suitable for children.' if request.is_family() else ''}
{'- This is a HONEYMOON — focus on romantic, scenic, intimate experiences.' if request.travel_type == 'honeymoon' else ''}
{'- Include ADVENTURE activities: trekking, water sports, outdoor activities.' if 'adventure' in request.preferences else ''}
{'- Include FOOD experiences: local markets, cooking classes, street food tours.' if 'food' in request.preferences else ''}
{'- Include CULTURAL experiences: temples, museums, historical sites.' if 'culture' in request.preferences else ''}
{'- Luxury experiences preferred.' if request.is_luxury() else ''}
 
Return the complete day-by-day itinerary as JSON. No other text."""
        
        result - chat_json(
            prompt = prompt, 
            system = SYSTEM_PROMPT,
            max_tokens = 3000,
        )

        if result.get("_parse_error"):
            print(f"[{self.name}] JSON parse issue - returning raw text")

            return {
                'days': [],
                'highlights': [],
                'local_transport_advice': '',
                'raw': result.get('raw', '')
            }
 
        return result
    
#self test
if __name__ == "__name__":
    from dotenv import load_dotenv
    load_dotenv()

    
    print("=" * 55)
    print("  itinerary_agent.py — self test")
    print("=" * 55)
 
    agent = ItineraryAgent()
 
    req = TravelRequest(
        destination   = "Goa",
        origin        = "Ahmedabad",
        budget        = 30000,
        duration_days = 5,
        travel_type   = "couple",
        passengers    = 2,
        start_date    = "2025-06-15",
        end_date      = "2025-06-20",
        preferences   = ["beach", "food"],
    )
 
    # Simulate hotel and flight results
    mock_hotel = {
        "recommended": {
            "name": "Goa Hotel",
            "area": "Baga Beach",
            "stars": 3,
        }
    }
    mock_flights = {
        "recommended": {
            "arrive_time": "2025-06-15 10:30",
            "depart_time": "2025-06-20 14:00",
        }
    }
 
    print(f"\n  Building {req.duration_days}-day itinerary for {req.destination}...")
    print("  (This calls Gemini — takes a few seconds)\n")
 
    result = agent.run(req, mock_hotel, mock_flights)
    days = result.get("days", [])
 
    if days:
        print(f"  Generated {len(days)} days:")
        for day in days:
            print(f"\n  Day {day['day']}: {day.get('title', '')}")
            print(f"  Theme: {day.get('theme', '')}")
            schedule = day.get("schedule", [])
            for item in schedule[:3]:   # show first 3 activities per day
                print(f"    {item.get('time','')} — {item.get('activity','')} "
                      f"({item.get('location','')})")
            meals = day.get("meals", {})
            if meals.get("dinner"):
                print(f"    Dinner: {meals['dinner'][:60]}...")
 
        highlights = result.get("highlights", [])
        if highlights:
            print(f"\n  Highlights:")
            for h in highlights:
                print(f"  • {h}")
 
        print(f"\n  Transport: {result.get('local_transport_advice','')}")
        print(f"\n  Itinerary generated successfully")
    else:
        print("  No days returned — check raw output:")
        print(result.get("raw", "")[:300])
 
    print("\n" + "=" * 55)
    print("  ItineraryAgent done. Moving to BudgetAgent...")
    print("=" * 55)
 