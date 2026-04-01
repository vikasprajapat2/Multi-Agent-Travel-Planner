import os 
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import Optional

from agents.planner import PlannerAgent
from memory.Session_store import SessionStore
from config import APP_HOST, APP_PORT

#APP setup

app = FastAPI(
    title= "Multi-Agent Travel Planner API",
    description= "AI-powered travel planning - flights , hotels, itinerary, budget",
    version = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"] 
)

planner = PlannerAgent()

# Pydantic request/ response models
class PlanRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ReplanRequest(BaseModel):
    session_id: str
    change: str
    label: Optional[str] = None

class sessionResponse(BaseModel):
    session_id: str

# Routes
@app.get("/")
def root():
    return {
        "status":   "running",
        "service":  "Multi-Agent Travel Planner",
        "version":  "1.0.0",
        "docs":     "http://localhost:8000/docs",
        "endpoints": {
            "POST /session":             "Create a new session",
            "POST /plan":                "Generate travel plan from text",
            "POST /replan":              "Update existing plan",
            "GET  /plan/{session_id}":   "Get latest plan",
            "GET  /compare/{session_id}":"Compare all plan versions",
            "GET  /history/{session_id}":"Get chat history",
            "GET  /export/{session_id}": "Export plan as text",
        }       
    }

@app.get("/health")
def health():
    return {
        'status': "ok",
        'active_sessions': SessionStore.active_count(),
    }

@app.post("/session", response_model= sessionResponse)
def create_session():
    session_id = SessionStore.create()
    return {'session_id': session_id} 

@app.post('/plan')
def create_plan(req: PlanRequest):
    session_id = req.session_id or SessionStore.create()
    try:
        plan = planner.plan(req.query, session_id)
        return {
            'session_id':  session_id,
            "plan": plan,
        }

    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"planning faild: {str(e)}")

@app.post('/replan')
def update_plan(req: ReplanRequest):
    session = SessionStore.get(req.session_id)
    if not session:
        raise HTTPException(
            status_code = 404,
            details = "Session not found or expired. create a new session first"
        )
    
    if not SessionStore.get_latest_request(req.session_id):
        raise HTTPException(
            status_code = 400,
            details = ":No existing plan found for this session. call Post/ plan first"
        )
    
    try :
        plan = planner.replan(req.session_id, req.change)
        if req.label:
            versions = SessionStore.get_plan_versions(req.session_id)
            if versions: 
                versions[-1].label = req.label

            return {
                "session_id": req.session_id,
                "plan": plan,
                "message": f'Plan updated: {req.chabge}',
            }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Re-planning failed: {str(e)}")
    
@app.get("/plan/{session_id}")
def get_plan(session_id: str):
    plan = SessionStore.get_latest_plan(session_id)
    if not plan:
        raise HTTPException(
            status_code=404,
            detail      = "No plan found for this session."
        )
    return {"session_id": session_id, "plan": plan}

@app.get("/compare/{session_id}")
def compare_plans(session_id: str):
    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
 
    return planner.compare_plans(session_id)


 
@app.get("/history/{session_id}")
def get_history(session_id: str):

    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
 
    return {
        "session_id": session_id,
        "messages":   SessionStore.get_messages(session_id),
        "plan_count": len(SessionStore.get_plan_versions(session_id)),
    }
 
@app.get("/export/{session_id}")
def export_plan(session_id: str):
    """
    Export the latest plan as formatted plain text.
 
    USE CASE:
        User wants to copy-paste their itinerary into WhatsApp, email, notes.
        Returns both the text and the raw plan dict.
    """
    plan = SessionStore.get_latest_plan(session_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found.")
 
    text = _format_plan_text(plan)
    return {
        "session_id": session_id,
        "text":       text,
        "plan":       plan,
    }

# text formatter (for / export endpoint)

def _format_plan_text(plan: dict) -> str:
    """
    Convert a plan dict to readable plain text.
    Used by /export and can be used for WhatsApp/email sharing.
    """
    lines = []
    sep   = "=" * 50
 
    lines.append(sep)
    lines.append(f"  {plan.get('trip_title','Travel Plan').upper()}")
    lines.append(sep)
    lines.append(f"Destination : {plan.get('destination','')}")
    lines.append(f"From        : {plan.get('origin','')}")
    lines.append(f"Duration    : {plan.get('duration','')}")
    lines.append(f"Dates       : {plan.get('dates','')}")
    lines.append(f"Travel type : {plan.get('travel_type','').title()}")
    lines.append("")
 
    # Flights
    flights = plan.get("flights", {})
    rec_f   = flights.get("recommended") or {}
    if rec_f:
        lines.append("✈  FLIGHT")
        lines.append(
            f"   {rec_f.get('airline','')} {rec_f.get('flight_number','')} | "
            f"{rec_f.get('depart_time','')} → {rec_f.get('arrive_time','')} | "
            f"₹{flights.get('round_trip_cost',0):,}"
        )
        lines.append("")
 
    # Hotel
    hotel = plan.get("hotel", {})
    rec_h = hotel.get("recommended") or {}
    if rec_h:
        stars = "★" * rec_h.get("stars", 0)
        lines.append("🏨  HOTEL")
        lines.append(
            f"   {rec_h.get('name','')} {stars} | "
            f"{rec_h.get('area','')} | "
            f"₹{hotel.get('per_night_cost',0):,}/night"
        )
        lines.append("")
 
    # Itinerary
    days = plan.get("itinerary", {}).get("days", [])
    if days:
        lines.append("📍  ITINERARY")
        for day in days:
            lines.append(f"\n  Day {day['day']}: {day.get('title','')}")
            for item in day.get("schedule", [])[:4]:
                lines.append(
                    f"   {item.get('time','')}  {item.get('activity','')} "
                    f"— {item.get('location','')}"
                )
            meals = day.get("meals", {})
            if meals.get("lunch"):
                lines.append(f"   Lunch : {meals['lunch'][:60]}")
            if meals.get("dinner"):
                lines.append(f"   Dinner: {meals['dinner'][:60]}")
        lines.append("")
 
    # Budget
    budget = plan.get("budget", {})
    if budget:
        lines.append("💰  BUDGET")
        breakdown = budget.get("breakdown", {})
        for cat, data in breakdown.items():
            cost = data.get("cost", 0)
            if cost > 0:
                lines.append(f"   {cat.replace('_',' ').title():<18} ₹{cost:,}")
        lines.append(f"   {'─'*28}")
        lines.append(f"   {'Total':<18} ₹{budget.get('total_cost',0):,}")
        lines.append(f"   {'Budget':<18} ₹{budget.get('total_budget',0):,}")
        surplus = budget.get('surplus_or_deficit', 0)
        sign = "+" if surplus >= 0 else ""
        lines.append(f"   {'Surplus':<18} {sign}₹{abs(surplus):,}")
        lines.append(f"   Status: {budget.get('status','').replace('_',' ').upper()}")
        lines.append("")
 
        tips = budget.get("optimisation_tips", [])
        if tips:
            lines.append("💡  MONEY-SAVING TIPS")
            for tip in tips:
                lines.append(f"   • {tip}")
            lines.append("")
 
    lines.append(sep)
    return "\n".join(lines)
 
 

# Run server

 
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  Starting Travel Planner API")
    print(f"  http://localhost:{APP_PORT}")
    print(f"  http://localhost:{APP_PORT}/docs  ← Swagger UI")
    print("=" * 50)
    uvicorn.run(
        "main:app",
        host   = APP_HOST,
        port   = APP_PORT,
        reload = True,    # auto-restart on file changes during development
    )
 