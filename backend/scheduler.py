import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from models import Pair, Symbol, BacktestJob
from jquants_client import JQuantsClient
from services.backtest_engine import BacktestEngine

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self):
        self.jquants_client = JQuantsClient()
        self.backtest_engine = BacktestEngine()
        self.running = False
        
    async def start(self):
        """スケジューラーを開始"""
        if self.running:
            return
            
        self.running = True
        logger.info("Task scheduler started")
        
        # 各タスクを並行実行
        tasks = [
            asyncio.create_task(self.market_data_sync_loop()),
            asyncio.create_task(self.pair_calculation_loop()),
            asyncio.create_task(self.backtest_processor_loop()),
            asyncio.create_task(self.cleanup_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
        finally:
            self.running = False
            
    async def stop(self):
        """スケジューラーを停止"""
        self.running = False
        logger.info("Task scheduler stopped")
        
    async def market_data_sync_loop(self):
        """市場データ同期ループ（平日9:00-15:30の間、5分間隔）"""
        while self.running:
            try:
                now = datetime.now()
                
                # 平日の市場時間内かチェック
                if self.is_market_hours(now):
                    await self.sync_market_data()
                    await asyncio.sleep(300)  # 5分間隔
                else:
                    # 市場時間外は1時間間隔
                    await asyncio.sleep(3600)
                    
            except Exception as e:
                logger.error(f"Error in market data sync loop: {e}")
                await asyncio.sleep(300)
                
    async def pair_calculation_loop(self):
        """ペア計算ループ（1分間隔）"""
        while self.running:
            try:
                await self.calculate_pair_metrics()
                await asyncio.sleep(60)  # 1分間隔
            except Exception as e:
                logger.error(f"Error in pair calculation loop: {e}")
                await asyncio.sleep(60)
                
    async def backtest_processor_loop(self):
        """バックテスト処理ループ（10秒間隔）"""
        while self.running:
            try:
                await self.process_pending_backtests()
                await asyncio.sleep(10)  # 10秒間隔
            except Exception as e:
                logger.error(f"Error in backtest processor loop: {e}")
                await asyncio.sleep(30)
                
    async def cleanup_loop(self):
        """クリーンアップループ（1時間間隔）"""
        while self.running:
            try:
                await self.cleanup_old_data()
                await asyncio.sleep(3600)  # 1時間間隔
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
                
    def is_market_hours(self, dt: datetime) -> bool:
        """市場時間内かどうかをチェック"""
        # 平日（月-金）かつ9:00-15:30の間
        if dt.weekday() >= 5:  # 土日
            return False
            
        market_open = dt.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = dt.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= dt <= market_close
        
    async def sync_market_data(self):
        """市場データを同期"""
        db = next(get_db())
        try:
            # 全ての監視対象銘柄を取得
            symbols = db.query(Symbol).all()
            
            for symbol in symbols:
                try:
                    # J-Quantsから最新価格を取得
                    price_data = await self.jquants_client.get_latest_price(symbol.symbol)
                    
                    if price_data:
                        # 価格データを更新
                        symbol.current_price = price_data.get('close')
                        symbol.change = price_data.get('change', 0)
                        symbol.change_percent = price_data.get('change_percent', 0)
                        symbol.volume = price_data.get('volume', 0)
                        symbol.updated_at = datetime.now()
                        
                        logger.debug(f"Updated price for {symbol.symbol}: {symbol.current_price}")
                        
                except Exception as e:
                    logger.error(f"Error updating price for {symbol.symbol}: {e}")
                    
            db.commit()
            logger.info(f"Market data sync completed for {len(symbols)} symbols")
            
        finally:
            db.close()
            
    async def calculate_pair_metrics(self):
        """ペアメトリクスを計算"""
        db = next(get_db())
        try:
            # アクティブなペアを取得
            active_pairs = db.query(Pair).filter(Pair.enabled == True).all()
            
            for pair in active_pairs:
                try:
                    # 銘柄の最新価格を取得
                    symbol_a = db.query(Symbol).filter(Symbol.symbol == pair.symbol_a).first()
                    symbol_b = db.query(Symbol).filter(Symbol.symbol == pair.symbol_b).first()
                    
                    if symbol_a and symbol_b and symbol_a.current_price and symbol_b.current_price:
                        # 相関係数とベータを計算
                        correlation = await self.calculate_correlation(pair.symbol_a, pair.symbol_b)
                        beta = await self.calculate_beta(pair.symbol_a, pair.symbol_b)
                        
                        # ペア情報を更新
                        pair.correlation = correlation
                        pair.beta = beta
                        pair.updated_at = datetime.now()
                        
                        logger.debug(f"Updated metrics for pair {pair.id}: corr={correlation:.3f}, beta={beta:.3f}")
                        
                except Exception as e:
                    logger.error(f"Error calculating metrics for pair {pair.id}: {e}")
                    
            db.commit()
            logger.debug(f"Pair metrics calculation completed for {len(active_pairs)} pairs")
            
        finally:
            db.close()
            
    async def calculate_correlation(self, symbol_a: str, symbol_b: str) -> float:
        """相関係数を計算"""
        # 実際の実装では過去の価格データから相関係数を計算
        # ここでは仮の値を返す
        import random
        return round(random.uniform(0.5, 0.9), 3)
        
    async def calculate_beta(self, symbol_a: str, symbol_b: str) -> float:
        """ベータを計算"""
        # 実際の実装では回帰分析でベータを計算
        # ここでは仮の値を返す
        import random
        return round(random.uniform(0.8, 1.2), 3)
        
    async def process_pending_backtests(self):
        """待機中のバックテストを処理"""
        db = next(get_db())
        try:
            # 待機中のバックテストジョブを取得
            pending_jobs = db.query(BacktestJob).filter(
                BacktestJob.status == 'pending'
            ).limit(1).all()  # 一度に1つずつ処理
            
            for job in pending_jobs:
                try:
                    logger.info(f"Processing backtest job {job.id}")
                    
                    # ステータスを実行中に更新
                    job.status = 'running'
                    job.started_at = datetime.now()
                    db.commit()
                    
                    # バックテストを実行
                    result = await self.backtest_engine.run_backtest(
                        symbol_a=job.symbol_a,
                        symbol_b=job.symbol_b,
                        start_date=job.start_date,
                        end_date=job.end_date,
                        params=job.params
                    )
                    
                    # 結果を保存
                    job.status = 'completed'
                    job.completed_at = datetime.now()
                    job.results = result
                    
                    logger.info(f"Backtest job {job.id} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error processing backtest job {job.id}: {e}")
                    job.status = 'failed'
                    job.error_message = str(e)
                    job.completed_at = datetime.now()
                    
                finally:
                    db.commit()
                    
        finally:
            db.close()
            
    async def cleanup_old_data(self):
        """古いデータをクリーンアップ"""
        db = next(get_db())
        try:
            # 30日以上前の完了済みアラートを削除
            cutoff_date = datetime.now() - timedelta(days=30)
            
            deleted_alerts = db.query(Alert).filter(
                Alert.status == 'completed',
                Alert.created_at < cutoff_date
            ).delete()
            
            # 90日以上前の失敗したバックテストジョブを削除
            cutoff_date_bt = datetime.now() - timedelta(days=90)
            
            deleted_jobs = db.query(BacktestJob).filter(
                BacktestJob.status == 'failed',
                BacktestJob.created_at < cutoff_date_bt
            ).delete()
            
            db.commit()
            
            if deleted_alerts > 0 or deleted_jobs > 0:
                logger.info(f"Cleanup completed: {deleted_alerts} alerts, {deleted_jobs} backtest jobs deleted")
                
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")
            db.rollback()
        finally:
            db.close()

# グローバルスケジューラーインスタンス
scheduler = TaskScheduler()

async def start_scheduler():
    """スケジューラーを開始"""
    await scheduler.start()
    
async def stop_scheduler():
    """スケジューラーを停止"""
    await scheduler.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        logger.info("Starting task scheduler...")
        try:
            await scheduler.start()
        except KeyboardInterrupt:
            logger.info("Shutting down task scheduler...")
            await scheduler.stop()
    
    asyncio.run(main())
