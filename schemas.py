"""
Database Schemas for AI Voice Agent SaaS

Each Pydantic model maps to a MongoDB collection with the lowercase class name.
- Agent -> "agent"
- Waitlist -> "waitlist"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Agent(BaseModel):
    """
    Voice agents offered in the catalog
    Collection: agent
    """
    name: str = Field(..., description="Agent name")
    persona: str = Field(..., description="Short persona description")
    use_case: str = Field(..., description="Primary use case e.g., Sales, Support, Booking")
    languages: List[str] = Field(default_factory=lambda: ["en"], description="Supported languages")
    starting_price: float = Field(..., ge=0, description="Monthly starting price in USD")
    demo_url: Optional[str] = Field(None, description="Optional URL to demo recording")
    avatar: Optional[str] = Field(None, description="Optional avatar or emoji")

class Waitlist(BaseModel):
    """
    Waitlist signups from the landing page
    Collection: waitlist
    """
    email: EmailStr
    company: Optional[str] = None
    interest: Optional[str] = Field(None, description="What they want to build")
