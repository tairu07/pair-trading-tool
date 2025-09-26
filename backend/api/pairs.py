"""
Pairs management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
import logging

from database import get_db
from models import Pair, Symbol, PairState, AlertRule, TimeFrame
from schemas.pairs import (
    PairCreate, PairResponse, PairUpdate, PairStateResponse,
    PairListResponse, PairDetailResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[PairListResponse])
async def get_pairs(
    enabled: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of trading pairs"""
    try:
        query = db.query(Pair)
        
        if enabled is not None:
            query = query.filter(Pair.enabled == enabled)
        
        pairs = query.offset(skip).limit(limit).all()
        
        result = []
        for pair in pairs:
            # Get latest state for each timeframe
            latest_states = {}
            for tf in TimeFrame:
                state = db.query(PairState).filter(
                    and_(
                        PairState.pair_id == pair.pair_id,
                        PairState.timeframe == tf
                    )
                ).order_by(PairState.updated_at.desc()).first()
                
                if state:
                    latest_states[tf.value] = PairStateResponse(
                        timeframe=state.timeframe,
                        z_score=state.z_score,
                        beta=state.beta,
                        correlation=state.correlation,
                        half_life=state.half_life,
                        price_a=state.price_a,
                        price_b=state.price_b,
                        spread=state.spread,
                        updated_at=state.updated_at
                    )
            
            result.append(PairListResponse(
                pair_id=pair.pair_id,
                symbol_a=pair.symbol_a,
                symbol_b=pair.symbol_b,
                name=pair.name,
                enabled=pair.enabled,
                created_at=pair.created_at,
                latest_states=latest_states
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching pairs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pairs"
        )


@router.post("/", response_model=PairResponse)
async def create_pair(
    pair_data: PairCreate,
    db: Session = Depends(get_db)
):
    """Create a new trading pair"""
    try:
        # Validate symbols exist
        symbol_a = db.query(Symbol).filter(Symbol.symbol == pair_data.symbol_a).first()
        symbol_b = db.query(Symbol).filter(Symbol.symbol == pair_data.symbol_b).first()
        
        if not symbol_a:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Symbol {pair_data.symbol_a} not found"
            )
        
        if not symbol_b:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Symbol {pair_data.symbol_b} not found"
            )
        
        # Check if pair already exists
        existing = db.query(Pair).filter(
            and_(
                Pair.symbol_a == pair_data.symbol_a,
                Pair.symbol_b == pair_data.symbol_b
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pair already exists"
            )
        
        # Create new pair
        pair = Pair(
            symbol_a=pair_data.symbol_a,
            symbol_b=pair_data.symbol_b,
            name=pair_data.name,
            description=pair_data.description,
            enabled=pair_data.enabled
        )
        
        db.add(pair)
        db.commit()
        db.refresh(pair)
        
        logger.info(f"Created new pair: {pair.symbol_a}/{pair.symbol_b}")
        
        return PairResponse(
            pair_id=pair.pair_id,
            symbol_a=pair.symbol_a,
            symbol_b=pair.symbol_b,
            name=pair.name,
            description=pair.description,
            enabled=pair.enabled,
            created_at=pair.created_at,
            updated_at=pair.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating pair: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pair"
        )


@router.get("/{pair_id}", response_model=PairDetailResponse)
async def get_pair(
    pair_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific pair"""
    try:
        pair = db.query(Pair).filter(Pair.pair_id == pair_id).first()
        
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pair not found"
            )
        
        # Get all states for this pair
        states = {}
        for tf in TimeFrame:
            state_history = db.query(PairState).filter(
                and_(
                    PairState.pair_id == pair_id,
                    PairState.timeframe == tf
                )
            ).order_by(PairState.updated_at.desc()).limit(100).all()
            
            if state_history:
                states[tf.value] = [
                    PairStateResponse(
                        timeframe=state.timeframe,
                        z_score=state.z_score,
                        beta=state.beta,
                        correlation=state.correlation,
                        half_life=state.half_life,
                        price_a=state.price_a,
                        price_b=state.price_b,
                        spread=state.spread,
                        updated_at=state.updated_at
                    ) for state in state_history
                ]
        
        # Get alert rules
        rules = db.query(AlertRule).filter(AlertRule.pair_id == pair_id).all()
        
        return PairDetailResponse(
            pair_id=pair.pair_id,
            symbol_a=pair.symbol_a,
            symbol_b=pair.symbol_b,
            name=pair.name,
            description=pair.description,
            enabled=pair.enabled,
            created_at=pair.created_at,
            updated_at=pair.updated_at,
            states=states,
            alert_rules_count=len(rules)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pair {pair_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pair details"
        )


@router.put("/{pair_id}", response_model=PairResponse)
async def update_pair(
    pair_id: UUID,
    pair_update: PairUpdate,
    db: Session = Depends(get_db)
):
    """Update a trading pair"""
    try:
        pair = db.query(Pair).filter(Pair.pair_id == pair_id).first()
        
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pair not found"
            )
        
        # Update fields
        update_data = pair_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pair, field, value)
        
        db.commit()
        db.refresh(pair)
        
        logger.info(f"Updated pair: {pair_id}")
        
        return PairResponse(
            pair_id=pair.pair_id,
            symbol_a=pair.symbol_a,
            symbol_b=pair.symbol_b,
            name=pair.name,
            description=pair.description,
            enabled=pair.enabled,
            created_at=pair.created_at,
            updated_at=pair.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pair {pair_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pair"
        )


@router.delete("/{pair_id}")
async def delete_pair(
    pair_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a trading pair"""
    try:
        pair = db.query(Pair).filter(Pair.pair_id == pair_id).first()
        
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pair not found"
            )
        
        db.delete(pair)
        db.commit()
        
        logger.info(f"Deleted pair: {pair_id}")
        
        return {"message": "Pair deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pair {pair_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pair"
        )
