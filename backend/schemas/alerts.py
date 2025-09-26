"""
Pydantic schemas for alerts API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from models import TimeFrame, AlertStatus


class AlertRuleCreate(BaseModel):
    """Schema for creating an alert rule"""
    pair_id: UUID = Field(..., description="Pair ID")
    timeframe: TimeFrame = Field(..., description="Timeframe")
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    params: Dict[str, Any] = Field(..., description="Rule parameters")
    enabled: bool = Field(True, description="Whether the rule is enabled")


class AlertRuleUpdate(BaseModel):
    """Schema for updating an alert rule"""
    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    params: Optional[Dict[str, Any]] = Field(None, description="Rule parameters")
    enabled: Optional[bool] = Field(None, description="Whether the rule is enabled")


class AlertRuleResponse(BaseModel):
    """Schema for alert rule response"""
    rule_id: UUID
    pair_id: UUID
    timeframe: TimeFrame
    name: str
    description: Optional[str]
    params: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Schema for alert response"""
    alert_id: UUID
    pair_id: UUID
    rule_id: UUID
    timeframe: TimeFrame
    message: str
    alert_type: Optional[str]
    z_score: Optional[float]
    beta: Optional[float]
    correlation: Optional[float]
    price_a: Optional[float]
    price_b: Optional[float]
    status: AlertStatus
    delivered_at: Optional[datetime]
    delivery_channels: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema for alert list response"""
    alert_id: UUID
    pair_id: UUID
    rule_id: UUID
    timeframe: TimeFrame
    message: str
    alert_type: Optional[str]
    z_score: Optional[float]
    beta: Optional[float]
    correlation: Optional[float]
    status: AlertStatus
    created_at: datetime
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True
