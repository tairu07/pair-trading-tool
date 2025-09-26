"""
Backtest API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
import asyncio

from database import get_db
from models import BacktestJob, BacktestResult, BacktestStatus
from schemas.backtest import (
    BacktestJobCreate, BacktestJobResponse, BacktestResultResponse,
    BacktestJobListResponse
)
from services.backtest_engine import BacktestEngine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/jobs", response_model=List[BacktestJobListResponse])
async def get_backtest_jobs(
    status_filter: Optional[BacktestStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of backtest jobs"""
    try:
        query = db.query(BacktestJob)
        
        if status_filter:
            query = query.filter(BacktestJob.status == status_filter)
        
        jobs = query.order_by(BacktestJob.created_at.desc()).offset(skip).limit(limit).all()
        
        return [
            BacktestJobListResponse(
                job_id=job.job_id,
                name=job.name,
                status=job.status,
                progress=job.progress,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                params=job.params
            ) for job in jobs
        ]
    
    except Exception as e:
        logger.error(f"Error fetching backtest jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch backtest jobs"
        )


@router.post("/jobs", response_model=BacktestJobResponse)
async def create_backtest_job(
    job_data: BacktestJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a new backtest job"""
    try:
        # Create job record
        job = BacktestJob(
            name=job_data.name,
            description=job_data.description,
            params=job_data.params.dict(),
            status=BacktestStatus.PENDING
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start backtest in background
        background_tasks.add_task(run_backtest, job.job_id)
        
        logger.info(f"Created backtest job: {job.job_id}")
        
        return BacktestJobResponse(
            job_id=job.job_id,
            name=job.name,
            description=job.description,
            params=job.params,
            status=job.status,
            progress=job.progress,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )
    
    except Exception as e:
        logger.error(f"Error creating backtest job: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backtest job"
        )


@router.get("/jobs/{job_id}", response_model=BacktestJobResponse)
async def get_backtest_job(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Get backtest job details"""
    try:
        job = db.query(BacktestJob).filter(BacktestJob.job_id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backtest job not found"
            )
        
        return BacktestJobResponse(
            job_id=job.job_id,
            name=job.name,
            description=job.description,
            params=job.params,
            status=job.status,
            progress=job.progress,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching backtest job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch backtest job"
        )


@router.get("/jobs/{job_id}/result", response_model=BacktestResultResponse)
async def get_backtest_result(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Get backtest result"""
    try:
        job = db.query(BacktestJob).filter(BacktestJob.job_id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backtest job not found"
            )
        
        if job.status != BacktestStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Backtest not completed yet"
            )
        
        result = db.query(BacktestResult).filter(BacktestResult.job_id == job_id).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backtest result not found"
            )
        
        return BacktestResultResponse(
            result_id=result.result_id,
            job_id=result.job_id,
            total_trades=result.total_trades,
            winning_trades=result.winning_trades,
            losing_trades=result.losing_trades,
            win_rate=result.win_rate,
            total_pnl=result.total_pnl,
            average_pnl=result.average_pnl,
            median_pnl=result.median_pnl,
            max_profit=result.max_profit,
            max_loss=result.max_loss,
            max_drawdown=result.max_drawdown,
            sharpe_ratio=result.sharpe_ratio,
            average_hold_days=result.average_hold_days,
            median_hold_days=result.median_hold_days,
            max_hold_days=result.max_hold_days,
            detailed_results=result.detailed_results,
            created_at=result.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching backtest result for {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch backtest result"
        )


@router.delete("/jobs/{job_id}")
async def delete_backtest_job(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a backtest job and its results"""
    try:
        job = db.query(BacktestJob).filter(BacktestJob.job_id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backtest job not found"
            )
        
        # Delete associated result if exists
        result = db.query(BacktestResult).filter(BacktestResult.job_id == job_id).first()
        if result:
            db.delete(result)
        
        db.delete(job)
        db.commit()
        
        logger.info(f"Deleted backtest job: {job_id}")
        
        return {"message": "Backtest job deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting backtest job {job_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete backtest job"
        )


async def run_backtest(job_id: UUID):
    """Run backtest in background"""
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        job = db.query(BacktestJob).filter(BacktestJob.job_id == job_id).first()
        if not job:
            logger.error(f"Backtest job {job_id} not found")
            return
        
        # Update job status
        job.status = BacktestStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Run backtest
        engine = BacktestEngine()
        result = await engine.run_backtest(job.params, job_id, db)
        
        # Update job status
        job.status = BacktestStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 1.0
        db.commit()
        
        logger.info(f"Backtest job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error running backtest {job_id}: {e}")
        
        # Update job with error
        job = db.query(BacktestJob).filter(BacktestJob.job_id == job_id).first()
        if job:
            job.status = BacktestStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
    
    finally:
        db.close()
