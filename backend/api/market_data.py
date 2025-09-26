"""
Market data API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
from datetime import datetime, timedelta

from database import get_db
from models import Symbol
from jquants_client import JQuantsClient
from schemas.market_data import (
    SymbolResponse, PriceDataResponse, SymbolCreate, SymbolUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()


def get_jquants_client():
    """Get J-Quants client instance"""
    refresh_token = os.getenv("J_QUANTS_REFRESH_TOKEN")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="J-Quants refresh token not configured"
        )
    return JQuantsClient(refresh_token)


@router.get("/symbols", response_model=List[SymbolResponse])
async def get_symbols(
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of symbols"""
    try:
        query = db.query(Symbol)
        
        if exchange:
            query = query.filter(Symbol.exchange == exchange)
        if sector:
            query = query.filter(Symbol.sector == sector)
        
        symbols = query.offset(skip).limit(limit).all()
        
        return [
            SymbolResponse(
                symbol=s.symbol,
                name=s.name,
                exchange=s.exchange,
                sector=s.sector,
                lot_size=s.lot_size,
                tick_size=s.tick_size,
                is_shortable=s.is_shortable,
                created_at=s.created_at,
                updated_at=s.updated_at
            ) for s in symbols
        ]
    
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch symbols"
        )


@router.post("/symbols", response_model=SymbolResponse)
async def create_symbol(
    symbol_data: SymbolCreate,
    db: Session = Depends(get_db)
):
    """Create a new symbol"""
    try:
        # Check if symbol already exists
        existing = db.query(Symbol).filter(Symbol.symbol == symbol_data.symbol).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbol already exists"
            )
        
        symbol = Symbol(**symbol_data.dict())
        db.add(symbol)
        db.commit()
        db.refresh(symbol)
        
        logger.info(f"Created new symbol: {symbol.symbol}")
        
        return SymbolResponse(
            symbol=symbol.symbol,
            name=symbol.name,
            exchange=symbol.exchange,
            sector=symbol.sector,
            lot_size=symbol.lot_size,
            tick_size=symbol.tick_size,
            is_shortable=symbol.is_shortable,
            created_at=symbol.created_at,
            updated_at=symbol.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating symbol: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create symbol"
        )


@router.get("/prices/{symbol}", response_model=List[PriceDataResponse])
async def get_price_data(
    symbol: str,
    days: int = 30,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """Get price data for a symbol"""
    try:
        async with get_jquants_client() as client:
            if from_date and to_date:
                # Use specific date range
                price_data = await client.get_daily_quotes(
                    code=symbol,
                    from_date=from_date,
                    to_date=to_date
                )
            else:
                # Use days parameter
                price_data = await client.get_price_history(symbol, days)
            
            return [
                PriceDataResponse(
                    date=p.date,
                    symbol=p.code,
                    open=p.open,
                    high=p.high,
                    low=p.low,
                    close=p.close,
                    volume=p.volume,
                    adjustment_close=p.adjustment_close
                ) for p in price_data if p.date and p.adjustment_close
            ]
    
    except Exception as e:
        logger.error(f"Error fetching price data for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch price data for {symbol}"
        )


@router.get("/prices/{symbol_a}/{symbol_b}", response_model=dict)
async def get_pair_price_data(
    symbol_a: str,
    symbol_b: str,
    days: int = 30
):
    """Get aligned price data for a pair of symbols"""
    try:
        async with get_jquants_client() as client:
            # Fetch data for both symbols
            prices_a = await client.get_price_history(symbol_a, days)
            prices_b = await client.get_price_history(symbol_b, days)
            
            # Align the data by date
            from jquants_client import align_price_series
            aligned_a, aligned_b = align_price_series(prices_a, prices_b)
            
            return {
                "symbol_a": symbol_a,
                "symbol_b": symbol_b,
                "data_points": len(aligned_a),
                "prices_a": [
                    PriceDataResponse(
                        date=p.date,
                        symbol=p.code,
                        open=p.open,
                        high=p.high,
                        low=p.low,
                        close=p.close,
                        volume=p.volume,
                        adjustment_close=p.adjustment_close
                    ) for p in aligned_a
                ],
                "prices_b": [
                    PriceDataResponse(
                        date=p.date,
                        symbol=p.code,
                        open=p.open,
                        high=p.high,
                        low=p.low,
                        close=p.close,
                        volume=p.volume,
                        adjustment_close=p.adjustment_close
                    ) for p in aligned_b
                ]
            }
    
    except Exception as e:
        logger.error(f"Error fetching pair data for {symbol_a}/{symbol_b}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pair data for {symbol_a}/{symbol_b}"
        )


@router.post("/symbols/sync")
async def sync_symbols_from_jquants(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync symbols from J-Quants API"""
    try:
        async def sync_task():
            async with get_jquants_client() as client:
                companies = await client.get_listed_info()
                
                synced_count = 0
                for company in companies:
                    symbol_code = company.get("Code")
                    if not symbol_code:
                        continue
                    
                    existing = db.query(Symbol).filter(Symbol.symbol == symbol_code).first()
                    if not existing:
                        symbol = Symbol(
                            symbol=symbol_code,
                            name=company.get("CompanyName", ""),
                            exchange="TSE",  # Default to TSE
                            sector=company.get("Sector17CodeName", ""),
                            lot_size=100,  # Default lot size
                            tick_size=1.0,  # Default tick size
                            is_shortable=True  # Default to shortable
                        )
                        db.add(symbol)
                        synced_count += 1
                
                db.commit()
                logger.info(f"Synced {synced_count} new symbols from J-Quants")
        
        background_tasks.add_task(sync_task)
        
        return {"message": "Symbol sync started in background"}
    
    except Exception as e:
        logger.error(f"Error starting symbol sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start symbol sync"
        )
