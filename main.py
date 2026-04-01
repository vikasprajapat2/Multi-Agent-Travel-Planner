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
    title= "Multi-Agent Travel Planner API"
    description= "AI-powered travel planning - flights , hotels, itinerary, budget",
    version = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
    allow_methods = ["*"]
    allow_headers = ["*"] 
)

Planner = PlannerAgent()

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
            status_code=404:
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