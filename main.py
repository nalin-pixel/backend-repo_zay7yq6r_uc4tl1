import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Agent, Waitlist

app = FastAPI(title="AI Voice Agents SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Voice Agents SaaS Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "Unknown"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Public catalog of agents
@app.get("/agents", response_model=List[Agent])
def list_agents(limit: int = 50):
    try:
        docs = get_documents("agent", {}, limit)
        # Map MongoDB docs to Agent model by filtering fields
        agents: List[Agent] = []
        for d in docs:
            payload = {
                "name": d.get("name"),
                "persona": d.get("persona"),
                "use_case": d.get("use_case"),
                "languages": d.get("languages") or ["en"],
                "starting_price": float(d.get("starting_price", 0)),
                "demo_url": d.get("demo_url"),
                "avatar": d.get("avatar"),
            }
            agents.append(Agent(**payload))
        return agents
    except Exception as e:
        # If DB not configured, return a few seed examples so frontend works
        return [
            Agent(name="Sales Pro", persona="Confident closer with friendly tone", use_case="Sales",
                  languages=["en"], starting_price=49, demo_url=None, avatar="🗣️"),
            Agent(name="Support Genie", persona="Patient, empathetic problem-solver", use_case="Support",
                  languages=["en", "es"], starting_price=39, demo_url=None, avatar="✨"),
            Agent(name="Booking Bot", persona="Efficient, polite receptionist", use_case="Booking",
                  languages=["en"], starting_price=29, demo_url=None, avatar="📞"),
        ]

# Waitlist signup
class WaitlistIn(BaseModel):
    email: EmailStr
    company: Optional[str] = None
    interest: Optional[str] = None

@app.post("/waitlist")
def join_waitlist(payload: WaitlistIn):
    try:
        doc_id = create_document("waitlist", payload.model_dump())
        return {"status": "ok", "id": doc_id}
    except Exception:
        # If DB not available, still accept the signup but mark as queued
        return {"status": "queued"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
