import os 
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath*(__file__))))

import streamlit as st
import requests
import json
import time

# Page config + styling 
set.set_page_config(
    page_title ='AI Travel Planner',
    page_icon  = "✈️",
    layout = 'wide',
    initial_sidebar_state= "expanded"
)

st.markdown("""
<style>
.metric-box {
    background: var(--background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.day-card {
    border-left: 3px solid #4f7cff;
    padding-left: 1rem;
    margin: 0.75rem 0;
}
.tip-box {
    background: rgba(255,193,7,0.1);
    border-left: 3px solid #ffc107;
    padding: 0.5rem 0.75rem;
    border-radius: 0 6px 6px 0;
    margin: 0.3rem 0;
    font-size: 0.88rem;
}
.status-ok  { color: #16a34a; font-weight: 600; }
.status-bad { color: #dc2626; font-weight: 600; }
.status-tight { color: #d97706; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Api helpers

def api_create_session() -> str | None:
    try: 
        r= requests.post(f"{API_BASE}/session", timeout=5)
        if r.status_code == 200:
            return r.json()["session_id"]
    except requests.exceptions.ConnectionError:
        st.error("Connot connect to API. make sure FastAPI is running: \n"
                 "`.venv\\Scripts\\python.exe -m uvicorn main:app --reload --port 8000`")
    return None

def api_plan(query: str, session_id: str) -> dict | None:
    try:
        r = requests.post(
            f"{API_BASE}/plan"
            json = {'query': query, "session_id": session_id},
            timeout=120,
        )
        if r.status_code == 200:
            return r.json().get("plan")
        st.error(f"API error {r.status_code}: {r.json().get('detail','Unknown error')}")
    except requests.exceptions.ConnectionError:
        st.error("Lost connection to API server.")
    except requests.exceptions.Timeout:
        st.error(" Request timed out. The agents are taking too long — try again.")
    return None

def api_replan(session_id: str, change: str) -> dict | None:
    try:
        r = requests.post(
            f"{API_BASE}/replan",
            json    = {"session_id": session_id, "change": change},
            timeout = 120,
        )
        if r.status_code == 200:
            return r.json().get("plan")
        st.error(f"Re-plan failed: {r.json().get('detail','')}")
    except Exception as e:
        st.error(f"Error: {e}")
    return None

def api_export(session_id: str) -> str:
    """Call GET /export/{session_id}. Returns plain text."""
    try:
        r = requests.get(f"{API_BASE}/export/{session_id}", timeout=10)
        if r.status_code == 200:
            return r.json().get("text", "")
    except Exception:
        pass
    return ""

def ensure_session():
    """Create a session if we don't have one yet."""
    if not st.session_state.session_id:
        sid = api_create_session()
        if sid:
            st.session_state.session_id = sid
 
 
def fmt_inr(val) -> str:
    """Format a number as Indian Rupees."""
    try:
        return f"₹{int(val):,}"
    except (TypeError, ValueError):
        return "₹0"
 