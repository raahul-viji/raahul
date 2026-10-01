from pydantic import BaseModel, Field

class HomePlan(BaseModel):
    budget: float = Field(gt=0)
    rooms: str
    quantities: str = ""
    style: str = ""

class PartyPlan(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0)
    event_type: str
    venue: str = ""
    food_preference: str = ""

class JewelryPlan(BaseModel):
    budget: float = Field(gt=0)
    occasion: str
    style: str = ""
    outfit_notes: str = ""
