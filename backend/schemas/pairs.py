"""
Pydantic schemas for pairs API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID

from models import TimeFrame


class PairCreate(BaseModel):
    """Schema for creating a new pair"""
    symbol_a: str = Field(..., description="First symbol in the pair")
    symbol_b: str = Field(..., description="Second symbol in the pair")
    name: Optional[str] = Field(None, description="Custom name for the pair")
    description: Optional[str] = Field(None, description="Description of the pair")
    enabled: bool = Field(True, description="Whether the pair is enabled for monitoring")


class PairUpdate(BaseModel):
    """Schema for updating a pair"""
    name: Optional[str] = Field(None, description="Custom name for the pair")
    description: Optional[str] = Field(None, description="Description of the pair")
    enabled: Optional[bool] = Field(None, description="Whether the pair is enabled for monitoring")


class PairResponse(BaseModel):
    """Schema for pair response"""
    pair_id: UUID
    symbol_a: str
    symbol_b: str
    name: Optional[str]
    description: Optional[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PairStateResponse(BaseModel):
    """Schema for pair state response"""
    timeframe: TimeFrame
    z_score: Optional[float]
    beta: Optional[float]
    correlation: Optional[float]
    half_life: Optional[float]
    price_a: Optional[float]
    price_b: Optional[float]
    spread: Optional[float]
    updated_at: datetime

    class Config:
        from_attributes = True


class PairListResponse(BaseModel):
    """Schema for pair list response"""
    pair_id: UUID
    symbol_a: str
    symbol_b: str
    name: Optional[str]
    enabled: bool
    created_at: datetime
    latest_states: Dict[str, PairStateResponse] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class PairDetailResponse(BaseModel):
    """Schema for detailed pair response"""
    pair_id: UUID
    symbol_a: str
    symbol_b: str
    name: Optional[str]
    description: Optional[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    states: Dict[str, List[PairStateResponse]] = Field(default_factory=dict)
    alert_rules_count: int

    class Config:
        from_attributes = True
