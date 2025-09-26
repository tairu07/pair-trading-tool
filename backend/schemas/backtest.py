"""
Pydantic schemas for backtest API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from models import BacktestStatus


class BacktestParams(BaseModel):
    """Backtest parameters"""
    symbol_a: str = Field(..., description="First symbol")
    symbol_b: str = Field(..., description="Second symbol")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    timeframe: str = Field("1d", description="Timeframe")
    entry_z: float = Field(2.0, description="Entry z-score threshold")
    exit_z: float = Field(0.2, description="Exit z-score threshold")
    stop_z: float = Field(3.5, description="Stop loss z-score threshold")
    max_hold_days: int = Field(30, description="Maximum holding period in days")
    lookback: int = Field(200, description="Lookback period for calculations")
    fee_bps: float = Field(1.0, description="Trading fee in basis points")
    slip_bps: float = Field(1.0, description="Slippage in basis points")
    borrow_bps_day: float = Field(0.0, description="Daily borrowing cost in basis points")


class BacktestJobCreate(BaseModel):
    """Schema for creating a backtest job"""
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    params: BacktestParams = Field(..., description="Backtest parameters")


class BacktestJobResponse(BaseModel):
    """Schema for backtest job response"""
    job_id: UUID
    name: str
    description: Optional[str]
    params: Dict[str, Any]
    status: BacktestStatus
    progress: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class BacktestJobListResponse(BaseModel):
    """Schema for backtest job list response"""
    job_id: UUID
    name: str
    status: BacktestStatus
    progress: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    params: Dict[str, Any]

    class Config:
        from_attributes = True


class BacktestResultResponse(BaseModel):
    """Schema for backtest result response"""
    result_id: UUID
    job_id: UUID
    total_trades: Optional[int]
    winning_trades: Optional[int]
    losing_trades: Optional[int]
    win_rate: Optional[float]
    total_pnl: Optional[float]
    average_pnl: Optional[float]
    median_pnl: Optional[float]
    max_profit: Optional[float]
    max_loss: Optional[float]
    max_drawdown: Optional[float]
    sharpe_ratio: Optional[float]
    average_hold_days: Optional[float]
    median_hold_days: Optional[float]
    max_hold_days: Optional[int]
    detailed_results: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
