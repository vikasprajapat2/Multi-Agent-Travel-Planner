import os
import sys 
import random 
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.diename(os.path.abspath(__file__)))

from config import USE_MOCK_APIS

# hotelOption dataclass

@dataclass
class HotelOption:
    name: str
    stars: int
    area: str
    price_per_night: int
    total_price: int
    rating: float 
    amenities: str 
    cancellation: str
    breakfast: bool 
    category: str

    def to_dect(self) -> dict:
        return asdict(self)
    
    def summary(self) -> str:
        start_str ="*" * self.stars
        bkfstn =" | Breakfast incl." if self.breakfast else ""
        return (
            f"{self.name} {starts_str} | {self.area} |"
            f"₹{self.price_per_night:,}/night | "
            f"Rating: {self.rating}/10{bkfst}"
        )
    
#data table 

# knows areas per destunation - give hotels a realistic location 
_AREAS: dict[str, list[str]] = {
    "goa":       ["Baga Beach", "Calangute", "Panjim", "Anjuna", "Colva Beach"],
    "delhi":     ["Connaught Place", "Karol Bagh", "Aerocity", "Paharganj", "South Delhi"],
    "mumbai":    ["Bandra", "Colaba", "Andheri", "Juhu Beach", "Powai"],
    "jaipur":    ["Pink City", "C-Scheme", "Vaishali Nagar", "Bani Park"],
    "manali":    ["Mall Road", "Old Manali", "Vashisht", "Solang Valley"],
    "kerala":    ["Varkala", "Kovalam", "Fort Kochi", "Munnar"],
    "agra":      ["Taj Ganj", "Fatehabad Road", "Civil Lines"],
    "bangkok":   ["Sukhumvit", "Silom", "Khao San Road", "Siam"],
    "dubai":     ["Downtown", "Dubai Marina", "Deira", "JBR"],
    "maldives":  ["North Malé Atoll", "South Malé Atoll", "Baa Atoll"],
    "default":   ["City Centre", "Old Town", "Tourist Area", "Lake Side"],    
}

# Hotel templates per tier
# Each tier has name suffixes, star rating, price range (INR/night), rating range, amenities
_TIERS: dict[str, dict] = {
    "budget": {
        "suffixes":  ["Inn", "Lodge", "Hostel", "Guesthouse", "Residency"],
        "stars":     2,
        "price":     (600, 2200),
        "rating":    (5.5, 7.2),
        "amenities": ["Free WiFi", "24hr Front Desk", "Air Conditioning", "TV"],
        "breakfast": False,
    },
    "mid": {
        "suffixes":  ["Hotel", "Suites", "Plaza", "Residency", "Inn"],
        "stars":     3,
        "price":     (2200, 6000),
        "rating":    (6.8, 8.4),
        "amenities": ["Free WiFi", "Swimming Pool", "Restaurant",
                      "Room Service", "Gym", "Parking"],
        "breakfast": True,
    },
    "luxury": {
        "suffixes":  ["Grand", "Palace", "Resort", "Marriott", "Taj"],
        "stars":     5,
        "price":     (7000, 28000),
        "rating":    (8.2, 9.8),
        "amenities": ["Free WiFi", "Infinity Pool", "Spa", "Fine Dining",
                      "Concierge", "Airport Transfer", "Gym",
                      "Business Centre", "Butler Service"],
        "breakfast": True,
    },
}

#mock search

def _night_count(check_in: str, nights_param: int) -> int:
     return max(nights_param)

def _mock_search(
        destination: str,
        check_in: str,
        nights: int,
        guests: int,
        max_per_nights: float | None = None,
        travel_type:  str = "couple",
        preference: list = "None",
) -> List[HotelOption]:
    
    preference = preference or []
    des_key = destination.lower().split(",")[0].strip()
    areas = _AREAS.get(dest_key, AREAS['default'])

    is_lixuary = "luxury" in preference or travel_type == "honeymoon"
    is_budget = "budget" in preference
    if is_lixuary:
       tier_order = ["luxury", "mid", "budget"]
    elif is_budget:
        tier_order = ["budget", "mid", "luxury"]
    else:
        tier_order = ["mid", "budget", "luxury"]

    random.seed(hash(destination.lower() + check_in) % 9999)

    option: list[HotelOption] = []

    for tier in tier_order:
        t = _TIERS[tier]
        area = random.choice(areas)

        city = destination.split(',')[0].title()
        suffix = random.choice(t['suffixes'])
        name = f'{city} {suffix}'

        pmin, pmax = t['price']
        price = random.randint(pmin, pmax)
        rating = round(random.uniform(*t[rating]), 1)

        #family surcharge
        if travel_type == "family":
            price = int(price * 1.3)
        
        if max_per_nights and price > max_per_nights:
            price = max(int(max_per_nights * 0.9), pmin)

        total = price * nights

        option.append(HostelOption(
            name            = name,
            stars           = t["stars"],
            area            = area,
            price_per_night = price,
            total_price     = total,
            rating          = rating,
            amenities       = t["amenities"],
            cancellation    = "Free cancellation up to 48h before check-in",
            breakfast       = t["breakfast"],
            category        = tier,           
        ))
    return option

# public interface
def search_hotels(
    destination:   str,
    check_in:      str,
    nights:        int,
    guests:        int         = 2,
    max_per_night: float | None = None,
    travel_type:   str         = "couple",
    preferences:   list        = None,
) -> list[dict]:
    if USE_MOCK_APIS:
        options = _mock_search(
            destination= check_in, nights, guests,,
            max_per_nights, travel_type, preference or [],
        )
    else:
        raise NotImplementedError(
            "Real hotel API not configured. "
            "Set USE_MOCK_APIS=true or implement _real_search()." 
        )

    return [h.to_dict() for h in options]


        