"""
Alerts API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from uuid import UUID
import logging

from database import get_db
from models import Alert, AlertRule, Pair, AlertStatus, TimeFrame
from schemas.alerts import (
    AlertRuleCreate, AlertRuleResponse, AlertRuleUpdate,
    AlertResponse, AlertListResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/rules", response_model=List[AlertRuleResponse])
async def get_alert_rules(
    pair_id: Optional[UUID] = None,
    timeframe: Optional[TimeFrame] = None,
    enabled: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of alert rules"""
    try:
        query = db.query(AlertRule)
        
        if pair_id:
            query = query.filter(AlertRule.pair_id == pair_id)
        if timeframe:
            query = query.filter(AlertRule.timeframe == timeframe)
        if enabled is not None:
            query = query.filter(AlertRule.enabled == enabled)
        
        rules = query.offset(skip).limit(limit).all()
        
        return [
            AlertRuleResponse(
                rule_id=rule.rule_id,
                pair_id=rule.pair_id,
                timeframe=rule.timeframe,
                name=rule.name,
                description=rule.description,
                params=rule.params,
                enabled=rule.enabled,
                created_at=rule.created_at,
                updated_at=rule.updated_at
            ) for rule in rules
        ]
    
    except Exception as e:
        logger.error(f"Error fetching alert rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert rules"
        )


@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert rule"""
    try:
        # Validate pair exists
        pair = db.query(Pair).filter(Pair.pair_id == rule_data.pair_id).first()
        if not pair:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pair not found"
            )
        
        # Create alert rule
        rule = AlertRule(
            pair_id=rule_data.pair_id,
            timeframe=rule_data.timeframe,
            name=rule_data.name,
            description=rule_data.description,
            params=rule_data.params,
            enabled=rule_data.enabled
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        logger.info(f"Created alert rule: {rule.rule_id}")
        
        return AlertRuleResponse(
            rule_id=rule.rule_id,
            pair_id=rule.pair_id,
            timeframe=rule.timeframe,
            name=rule.name,
            description=rule.description,
            params=rule.params,
            enabled=rule.enabled,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert rule"
        )


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Get alert rule details"""
    try:
        rule = db.query(AlertRule).filter(AlertRule.rule_id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        
        return AlertRuleResponse(
            rule_id=rule.rule_id,
            pair_id=rule.pair_id,
            timeframe=rule.timeframe,
            name=rule.name,
            description=rule.description,
            params=rule.params,
            enabled=rule.enabled,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert rule"
        )


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: UUID,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert rule"""
    try:
        rule = db.query(AlertRule).filter(AlertRule.rule_id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        
        # Update fields
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        db.commit()
        db.refresh(rule)
        
        logger.info(f"Updated alert rule: {rule_id}")
        
        return AlertRuleResponse(
            rule_id=rule.rule_id,
            pair_id=rule.pair_id,
            timeframe=rule.timeframe,
            name=rule.name,
            description=rule.description,
            params=rule.params,
            enabled=rule.enabled,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert rule {rule_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert rule"
        )


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an alert rule"""
    try:
        rule = db.query(AlertRule).filter(AlertRule.rule_id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        
        db.delete(rule)
        db.commit()
        
        logger.info(f"Deleted alert rule: {rule_id}")
        
        return {"message": "Alert rule deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert rule {rule_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert rule"
        )


@router.get("/", response_model=List[AlertListResponse])
async def get_alerts(
    pair_id: Optional[UUID] = None,
    rule_id: Optional[UUID] = None,
    status_filter: Optional[AlertStatus] = None,
    alert_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of alerts"""
    try:
        query = db.query(Alert)
        
        if pair_id:
            query = query.filter(Alert.pair_id == pair_id)
        if rule_id:
            query = query.filter(Alert.rule_id == rule_id)
        if status_filter:
            query = query.filter(Alert.status == status_filter)
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
        
        return [
            AlertListResponse(
                alert_id=alert.alert_id,
                pair_id=alert.pair_id,
                rule_id=alert.rule_id,
                timeframe=alert.timeframe,
                message=alert.message,
                alert_type=alert.alert_type,
                z_score=alert.z_score,
                beta=alert.beta,
                correlation=alert.correlation,
                status=alert.status,
                created_at=alert.created_at,
                delivered_at=alert.delivered_at
            ) for alert in alerts
        ]
    
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alerts"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: Session = Depends(get_db)
):
    """Get alert details"""
    try:
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return AlertResponse(
            alert_id=alert.alert_id,
            pair_id=alert.pair_id,
            rule_id=alert.rule_id,
            timeframe=alert.timeframe,
            message=alert.message,
            alert_type=alert.alert_type,
            z_score=alert.z_score,
            beta=alert.beta,
            correlation=alert.correlation,
            price_a=alert.price_a,
            price_b=alert.price_b,
            status=alert.status,
            delivered_at=alert.delivered_at,
            delivery_channels=alert.delivery_channels,
            created_at=alert.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert"
        )
