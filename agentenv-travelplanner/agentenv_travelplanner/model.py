from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class CreateResponse(BaseModel):
    """Response for environment creation result"""
    id: int


class StepQuery(BaseModel):
    """Data model for step requests"""
    env_idx: int
    action: str


class StepResponse(BaseModel):
    """Data model for step responses"""
    observation: str
    reward: float
    done: bool
    info: Dict[str, Any]


class ResetQuery(BaseModel):
    """Data model for reset requests"""
    env_idx: int
    query: str
    use_react_agent: Optional[bool] = True


class ResetResponse(BaseModel):
    """Data model for reset responses"""
    observation: str
    info: Dict[str, Any]


class ObservationResponse(BaseModel):
    """Data model for observation responses"""
    observation: str


class InfoResponse(BaseModel):
    """Data model for info responses"""
    info: Dict[str, Any] 