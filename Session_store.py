import time 
from dataclasses import dataclass, asdict
from typing import Any

from config import SESSION_TTL_SECONDS, TravelRequest

@dataclass
class PlanVersion:
    """One saved snapshot of a travel plane """

    version_id: str  # short unique ID like "a3f8b2c1"
    label: str # human-readable: "budget plan", 'Luxury plan
    created_at: float # unix timestamp - time()
    request : dict # travelRequest converted to dict via asdict()
    request : dict # full plan output form plannerAgent
    total_cost: float # extracted from result['budget"]["total_cost"]


if __name__ == "__main__":
    print("=" * 55)
    print("  session_store.py — self test")
    print("=" * 55)
 
   