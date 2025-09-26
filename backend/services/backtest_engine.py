"""
Backtest engine for pair trading strategies
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from uuid import UUID
from sqlalchemy.orm import Session

from jquants_client import JQuantsClient, align_price_series, calculate_returns
from models import BacktestResult

logger = logging.getLogger(__name__)


class Trade:
    """Represents a single trade"""
    def __init__(self, entry_date: str, entry_z: float, direction: str):
        self.entry_date = entry_date
        self.entry_z = entry_z
        self.direction = direction  # 'long' or 'short'
        self.exit_date: Optional[str] = None
        self.exit_z: Optional[float] = None
        self.exit_reason: Optional[str] = None
        self.pnl: Optional[float] = None
        self.hold_days: Optional[int] = None
        self.entry_price_a: Optional[float] = None
        self.entry_price_b: Optional[float] = None
        self.exit_price_a: Optional[float] = None
        self.exit_price_b: Optional[float] = None


class BacktestEngine:
    """Backtest engine for pair trading strategies"""
    
    def __init__(self):
        self.refresh_token = os.getenv("J_QUANTS_REFRESH_TOKEN")
        if not self.refresh_token:
            raise ValueError("J_QUANTS_REFRESH_TOKEN environment variable not set")
    
    async def run_backtest(self, params: Dict[str, Any], job_id: UUID, db: Session) -> BacktestResult:
        """
        Run backtest with given parameters
        
        Args:
            params: Backtest parameters
            job_id: Job ID for tracking
            db: Database session
        
        Returns:
            BacktestResult object
        """
        try:
            logger.info(f"Starting backtest job {job_id}")
            
            # Extract parameters
            symbol_a = params["symbol_a"]
            symbol_b = params["symbol_b"]
            start_date = params["start_date"]
            end_date = params["end_date"]
            entry_z = params.get("entry_z", 2.0)
            exit_z = params.get("exit_z", 0.2)
            stop_z = params.get("stop_z", 3.5)
            max_hold_days = params.get("max_hold_days", 30)
            lookback = params.get("lookback", 200)
            fee_bps = params.get("fee_bps", 1.0)
            slip_bps = params.get("slip_bps", 1.0)
            borrow_bps_day = params.get("borrow_bps_day", 0.0)
            
            # Fetch price data
            async with JQuantsClient(self.refresh_token) as client:
                # Get extended date range to ensure enough lookback data
                extended_start = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=lookback + 100)
                extended_start_str = extended_start.strftime("%Y-%m-%d")
                
                prices_a = await client.get_daily_quotes(
                    code=symbol_a,
                    from_date=extended_start_str,
                    to_date=end_date
                )
                
                prices_b = await client.get_daily_quotes(
                    code=symbol_b,
                    from_date=extended_start_str,
                    to_date=end_date
                )
            
            # Align price series
            aligned_a, aligned_b = align_price_series(prices_a, prices_b)
            
            if len(aligned_a) < lookback + 50:
                raise ValueError(f"Insufficient data: only {len(aligned_a)} data points available")
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame({
                'date': [p.date for p in aligned_a],
                'price_a': [p.adjustment_close for p in aligned_a],
                'price_b': [p.adjustment_close for p in aligned_b]
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            
            # Calculate returns and statistics
            df['return_a'] = df['price_a'].pct_change()
            df['return_b'] = df['price_b'].pct_change()
            
            # Calculate rolling statistics
            df['beta'] = df['return_a'].rolling(lookback).cov(df['return_b']) / df['return_b'].rolling(lookback).var()
            df['correlation'] = df['return_a'].rolling(lookback).corr(df['return_b'])
            
            # Calculate spread and z-score
            df['spread'] = df['price_a'] - df['beta'] * df['price_b']
            df['spread_mean'] = df['spread'].rolling(lookback).mean()
            df['spread_std'] = df['spread'].rolling(lookback).std()
            df['z_score'] = (df['spread'] - df['spread_mean']) / df['spread_std']
            
            # Filter to backtest period
            backtest_start = pd.to_datetime(start_date)
            backtest_end = pd.to_datetime(end_date)
            backtest_df = df[(df.index >= backtest_start) & (df.index <= backtest_end)].copy()
            
            # Run trading simulation
            trades = self._simulate_trades(
                backtest_df, entry_z, exit_z, stop_z, max_hold_days
            )
            
            # Calculate performance metrics
            results = self._calculate_performance(
                trades, fee_bps, slip_bps, borrow_bps_day
            )
            
            # Create detailed results
            detailed_results = {
                "trades": [self._trade_to_dict(trade) for trade in trades],
                "equity_curve": self._calculate_equity_curve(trades),
                "monthly_returns": self._calculate_monthly_returns(trades),
                "parameters": params
            }
            
            # Save results to database
            result = BacktestResult(
                job_id=job_id,
                total_trades=results["total_trades"],
                winning_trades=results["winning_trades"],
                losing_trades=results["losing_trades"],
                win_rate=results["win_rate"],
                total_pnl=results["total_pnl"],
                average_pnl=results["average_pnl"],
                median_pnl=results["median_pnl"],
                max_profit=results["max_profit"],
                max_loss=results["max_loss"],
                max_drawdown=results["max_drawdown"],
                sharpe_ratio=results["sharpe_ratio"],
                average_hold_days=results["average_hold_days"],
                median_hold_days=results["median_hold_days"],
                max_hold_days=results["max_hold_days"],
                detailed_results=detailed_results
            )
            
            db.add(result)
            db.commit()
            db.refresh(result)
            
            logger.info(f"Backtest job {job_id} completed with {results['total_trades']} trades")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in backtest job {job_id}: {e}")
            raise
    
    def _simulate_trades(
        self, 
        df: pd.DataFrame, 
        entry_z: float, 
        exit_z: float, 
        stop_z: float, 
        max_hold_days: int
    ) -> List[Trade]:
        """Simulate trading based on z-score signals"""
        trades = []
        current_trade: Optional[Trade] = None
        
        for i, (date, row) in enumerate(df.iterrows()):
            if pd.isna(row['z_score']) or pd.isna(row['beta']):
                continue
            
            date_str = date.strftime('%Y-%m-%d')
            z_score = row['z_score']
            
            # Check for new entry signals
            if current_trade is None:
                if z_score >= entry_z:
                    # Short signal (expect mean reversion)
                    current_trade = Trade(date_str, z_score, 'short')
                    current_trade.entry_price_a = row['price_a']
                    current_trade.entry_price_b = row['price_b']
                elif z_score <= -entry_z:
                    # Long signal (expect mean reversion)
                    current_trade = Trade(date_str, z_score, 'long')
                    current_trade.entry_price_a = row['price_a']
                    current_trade.entry_price_b = row['price_b']
            
            # Check for exit signals
            elif current_trade is not None:
                should_exit = False
                exit_reason = None
                
                # Check for mean reversion exit
                if abs(z_score) <= exit_z:
                    should_exit = True
                    exit_reason = "mean_reversion"
                
                # Check for stop loss
                elif ((current_trade.direction == 'short' and z_score >= stop_z) or
                      (current_trade.direction == 'long' and z_score <= -stop_z)):
                    should_exit = True
                    exit_reason = "stop_loss"
                
                # Check for maximum holding period
                entry_date = pd.to_datetime(current_trade.entry_date)
                hold_days = (date - entry_date).days
                if hold_days >= max_hold_days:
                    should_exit = True
                    exit_reason = "max_hold"
                
                if should_exit:
                    current_trade.exit_date = date_str
                    current_trade.exit_z = z_score
                    current_trade.exit_reason = exit_reason
                    current_trade.exit_price_a = row['price_a']
                    current_trade.exit_price_b = row['price_b']
                    current_trade.hold_days = hold_days
                    
                    # Calculate PnL
                    current_trade.pnl = self._calculate_trade_pnl(current_trade, row['beta'])
                    
                    trades.append(current_trade)
                    current_trade = None
        
        return trades
    
    def _calculate_trade_pnl(self, trade: Trade, exit_beta: float) -> float:
        """Calculate PnL for a single trade"""
        if not all([trade.entry_price_a, trade.entry_price_b, trade.exit_price_a, trade.exit_price_b]):
            return 0.0
        
        # Calculate returns for each leg
        return_a = (trade.exit_price_a - trade.entry_price_a) / trade.entry_price_a
        return_b = (trade.exit_price_b - trade.entry_price_b) / trade.entry_price_b
        
        # Pair trading PnL calculation
        if trade.direction == 'long':
            # Long A, Short B (expecting positive spread)
            pnl = return_a - exit_beta * return_b
        else:
            # Short A, Long B (expecting negative spread)
            pnl = -return_a + exit_beta * return_b
        
        return pnl
    
    def _calculate_performance(
        self, 
        trades: List[Trade], 
        fee_bps: float, 
        slip_bps: float, 
        borrow_bps_day: float
    ) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_pnl": 0.0,
                "median_pnl": 0.0,
                "max_profit": 0.0,
                "max_loss": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "average_hold_days": 0.0,
                "median_hold_days": 0.0,
                "max_hold_days": 0
            }
        
        # Adjust PnL for costs
        adjusted_pnls = []
        hold_days_list = []
        
        for trade in trades:
            if trade.pnl is None or trade.hold_days is None:
                continue
            
            # Transaction costs (entry + exit)
            transaction_cost = 2 * (fee_bps + slip_bps) / 10000
            
            # Borrowing costs (for short positions)
            borrow_cost = 0.0
            if trade.direction == 'short':
                borrow_cost = (borrow_bps_day / 10000) * trade.hold_days
            
            adjusted_pnl = trade.pnl - transaction_cost - borrow_cost
            adjusted_pnls.append(adjusted_pnl)
            hold_days_list.append(trade.hold_days)
        
        if not adjusted_pnls:
            return self._empty_performance_dict()
        
        # Calculate metrics
        total_pnl = sum(adjusted_pnls)
        winning_trades = sum(1 for pnl in adjusted_pnls if pnl > 0)
        losing_trades = sum(1 for pnl in adjusted_pnls if pnl <= 0)
        win_rate = winning_trades / len(adjusted_pnls) if adjusted_pnls else 0
        
        # Calculate drawdown
        cumulative_pnl = np.cumsum(adjusted_pnls)
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = running_max - cumulative_pnl
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        # Calculate Sharpe ratio (annualized)
        if len(adjusted_pnls) > 1:
            avg_return = np.mean(adjusted_pnls)
            std_return = np.std(adjusted_pnls, ddof=1)
            if std_return > 0:
                # Assume average trade frequency for annualization
                avg_hold_days = np.mean(hold_days_list)
                trades_per_year = 252 / avg_hold_days if avg_hold_days > 0 else 1
                sharpe_ratio = (avg_return * np.sqrt(trades_per_year)) / std_return
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        return {
            "total_trades": len(trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "average_pnl": np.mean(adjusted_pnls),
            "median_pnl": np.median(adjusted_pnls),
            "max_profit": np.max(adjusted_pnls),
            "max_loss": np.min(adjusted_pnls),
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "average_hold_days": np.mean(hold_days_list),
            "median_hold_days": np.median(hold_days_list),
            "max_hold_days": int(np.max(hold_days_list))
        }
    
    def _empty_performance_dict(self) -> Dict[str, Any]:
        """Return empty performance dictionary"""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "average_pnl": 0.0,
            "median_pnl": 0.0,
            "max_profit": 0.0,
            "max_loss": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "average_hold_days": 0.0,
            "median_hold_days": 0.0,
            "max_hold_days": 0
        }
    
    def _trade_to_dict(self, trade: Trade) -> Dict[str, Any]:
        """Convert Trade object to dictionary"""
        return {
            "entry_date": trade.entry_date,
            "exit_date": trade.exit_date,
            "direction": trade.direction,
            "entry_z": trade.entry_z,
            "exit_z": trade.exit_z,
            "exit_reason": trade.exit_reason,
            "pnl": trade.pnl,
            "hold_days": trade.hold_days,
            "entry_price_a": trade.entry_price_a,
            "entry_price_b": trade.entry_price_b,
            "exit_price_a": trade.exit_price_a,
            "exit_price_b": trade.exit_price_b
        }
    
    def _calculate_equity_curve(self, trades: List[Trade]) -> List[Dict[str, Any]]:
        """Calculate equity curve from trades"""
        equity_curve = []
        cumulative_pnl = 0.0
        
        for trade in trades:
            if trade.pnl is not None and trade.exit_date:
                cumulative_pnl += trade.pnl
                equity_curve.append({
                    "date": trade.exit_date,
                    "cumulative_pnl": cumulative_pnl,
                    "trade_pnl": trade.pnl
                })
        
        return equity_curve
    
    def _calculate_monthly_returns(self, trades: List[Trade]) -> Dict[str, float]:
        """Calculate monthly returns"""
        monthly_pnl = {}
        
        for trade in trades:
            if trade.pnl is not None and trade.exit_date:
                month_key = trade.exit_date[:7]  # YYYY-MM
                if month_key not in monthly_pnl:
                    monthly_pnl[month_key] = 0.0
                monthly_pnl[month_key] += trade.pnl
        
        return monthly_pnl
