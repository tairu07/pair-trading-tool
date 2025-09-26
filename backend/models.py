"""
SQLAlchemy models for the pair trading application
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, 
    ForeignKey, Index, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from database import Base


class TimeFrame(str, enum.Enum):
    """Time frame enumeration"""
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"


class BacktestStatus(str, enum.Enum):
    """Backtest job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Symbol(Base):
    """Symbol master table"""
    __tablename__ = "symbols"

    symbol = Column(String(20), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    exchange = Column(String(10), nullable=False)
    sector = Column(String(100))
    lot_size = Column(Integer, default=100)
    tick_size = Column(Float, default=1.0)
    is_shortable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pairs_a = relationship("Pair", foreign_keys="Pair.symbol_a", back_populates="symbol_a_ref")
    pairs_b = relationship("Pair", foreign_keys="Pair.symbol_b", back_populates="symbol_b_ref")

    def __repr__(self):
        return f"<Symbol(symbol='{self.symbol}', name='{self.name}')>"


class Pair(Base):
    """Trading pair definition"""
    __tablename__ = "pairs"

    pair_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    symbol_a = Column(String(20), ForeignKey("symbols.symbol"), nullable=False)
    symbol_b = Column(String(20), ForeignKey("symbols.symbol"), nullable=False)
    name = Column(String(100))  # Optional custom name for the pair
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    symbol_a_ref = relationship("Symbol", foreign_keys=[symbol_a])
    symbol_b_ref = relationship("Symbol", foreign_keys=[symbol_b])
    states = relationship("PairState", back_populates="pair")
    rules = relationship("AlertRule", back_populates="pair")
    alerts = relationship("Alert", back_populates="pair")

    # Indexes
    __table_args__ = (
        Index("idx_pairs_symbols", "symbol_a", "symbol_b"),
        Index("idx_pairs_enabled", "enabled"),
    )

    def __repr__(self):
        return f"<Pair(pair_id='{self.pair_id}', symbols='{self.symbol_a}/{self.symbol_b}')>"


class PairState(Base):
    """Current state of a trading pair"""
    __tablename__ = "pair_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pair_id = Column(UUID(as_uuid=True), ForeignKey("pairs.pair_id"), nullable=False)
    timeframe = Column(SQLEnum(TimeFrame), nullable=False)
    
    # Statistical measures
    z_score = Column(Float)
    beta = Column(Float)
    correlation = Column(Float)
    half_life = Column(Float)  # in days
    
    # Price information
    price_a = Column(Float)
    price_b = Column(Float)
    spread = Column(Float)
    
    # Lookback period used for calculations
    lookback_periods = Column(Integer, default=200)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pair = relationship("Pair", back_populates="states")

    # Indexes
    __table_args__ = (
        Index("idx_pair_states_pair_tf", "pair_id", "timeframe"),
        Index("idx_pair_states_updated", "updated_at"),
    )

    def __repr__(self):
        return f"<PairState(pair_id='{self.pair_id}', tf='{self.timeframe}', z={self.z_score})>"


class AlertRule(Base):
    """Alert rule configuration"""
    __tablename__ = "alert_rules"

    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pair_id = Column(UUID(as_uuid=True), ForeignKey("pairs.pair_id"), nullable=False)
    timeframe = Column(SQLEnum(TimeFrame), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Rule parameters (stored as JSON)
    params = Column(JSON, nullable=False)
    # Example params structure:
    # {
    #   "entry_z_threshold": 2.0,
    #   "exit_z_threshold": 0.2,
    #   "stop_z_threshold": 3.5,
    #   "correlation_threshold": 0.7,
    #   "cooldown_minutes": 60
    # }
    
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pair = relationship("Pair", back_populates="rules")
    alerts = relationship("Alert", back_populates="rule")

    # Indexes
    __table_args__ = (
        Index("idx_alert_rules_pair_tf", "pair_id", "timeframe"),
        Index("idx_alert_rules_enabled", "enabled"),
    )

    def __repr__(self):
        return f"<AlertRule(rule_id='{self.rule_id}', name='{self.name}')>"


class Alert(Base):
    """Alert log"""
    __tablename__ = "alerts"

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pair_id = Column(UUID(as_uuid=True), ForeignKey("pairs.pair_id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.rule_id"), nullable=False)
    timeframe = Column(SQLEnum(TimeFrame), nullable=False)
    
    # Alert details
    message = Column(Text, nullable=False)
    alert_type = Column(String(50))  # e.g., "entry_long", "entry_short", "exit", "stop"
    
    # Market data at alert time
    z_score = Column(Float)
    beta = Column(Float)
    correlation = Column(Float)
    price_a = Column(Float)
    price_b = Column(Float)
    
    # Status and delivery
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    delivered_at = Column(DateTime)
    delivery_channels = Column(JSON)  # List of channels where alert was sent
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    pair = relationship("Pair", back_populates="alerts")
    rule = relationship("AlertRule", back_populates="alerts")

    # Indexes
    __table_args__ = (
        Index("idx_alerts_pair_created", "pair_id", "created_at"),
        Index("idx_alerts_status", "status"),
        Index("idx_alerts_type", "alert_type"),
    )

    def __repr__(self):
        return f"<Alert(alert_id='{self.alert_id}', type='{self.alert_type}')>"


class BacktestJob(Base):
    """Backtest job management"""
    __tablename__ = "backtest_jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200))
    description = Column(Text)
    
    # Job parameters (stored as JSON)
    params = Column(JSON, nullable=False)
    # Example params structure:
    # {
    #   "symbol_a": "7203",
    #   "symbol_b": "7267",
    #   "start_date": "2023-01-01",
    #   "end_date": "2023-12-31",
    #   "timeframe": "1d",
    #   "entry_z": 2.0,
    #   "exit_z": 0.2,
    #   "stop_z": 3.5,
    #   "max_hold_days": 30,
    #   "lookback": 200,
    #   "fee_bps": 1.0,
    #   "slip_bps": 1.0,
    #   "borrow_bps_day": 0.0
    # }
    
    status = Column(SQLEnum(BacktestStatus), default=BacktestStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Relationships
    result = relationship("BacktestResult", back_populates="job", uselist=False)

    # Indexes
    __table_args__ = (
        Index("idx_backtest_jobs_status", "status"),
        Index("idx_backtest_jobs_created", "created_at"),
    )

    def __repr__(self):
        return f"<BacktestJob(job_id='{self.job_id}', status='{self.status}')>"


class BacktestResult(Base):
    """Backtest results"""
    __tablename__ = "backtest_results"

    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("backtest_jobs.job_id"), nullable=False)
    
    # Summary statistics
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(Float)
    
    # PnL statistics
    total_pnl = Column(Float)
    average_pnl = Column(Float)
    median_pnl = Column(Float)
    max_profit = Column(Float)
    max_loss = Column(Float)
    
    # Risk metrics
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    
    # Holding period statistics
    average_hold_days = Column(Float)
    median_hold_days = Column(Float)
    max_hold_days = Column(Integer)
    
    # Detailed results (stored as JSON)
    detailed_results = Column(JSON)
    # Contains trade-by-trade results, equity curve, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("BacktestJob", back_populates="result")

    def __repr__(self):
        return f"<BacktestResult(result_id='{self.result_id}', trades={self.total_trades})>"
