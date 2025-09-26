"""
Pydantic schemas for market data API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SymbolCreate(BaseModel):
    """Schema for creating a new symbol"""
    symbol: str = Field(..., description="Symbol code")
    name: str = Field(..., description="Company name")
    exchange: str = Field(..., description="Exchange code")
    sector: Optional[str] = Field(None, description="Sector name")
    lot_size: int = Field(100, description="Lot size")
    tick_size: float = Field(1.0, description="Tick size")
    is_shortable: bool = Field(True, description="Whether the symbol is shortable")


class SymbolUpdate(BaseModel):
    """Schema for updating a symbol"""
    name: Optional[str] = Field(None, description="Company name")
    exchange: Optional[str] = Field(None, description="Exchange code")
    sector: Optional[str] = Field(None, description="Sector name")
    lot_size: Optional[int] = Field(None, description="Lot size")
    tick_size: Optional[float] = Field(None, description="Tick size")
    is_shortable: Optional[bool] = Field(None, description="Whether the symbol is shortable")


class SymbolResponse(BaseModel):
    """Schema for symbol response"""
    symbol: str
    name: str
    exchange: str
    sector: Optional[str]
    lot_size: int
    tick_size: float
    is_shortable: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PriceDataResponse(BaseModel):
    """Schema for price data response"""
    date: str
    symbol: str
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[float]
    adjustment_close: Optional[float]

    class Config:
        from_attributes = True
