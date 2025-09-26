import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
import websockets
from websockets.server import WebSocketServerProtocol
from sqlalchemy.orm import Session
from database import get_db
from models import Pair, PairState, Alert
from jquants_client import JQuantsClient

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: Set[WebSocketServerProtocol] = set()
        self.jquants_client = JQuantsClient()
        self.monitoring_active = False
        
    async def register(self, websocket: WebSocketServerProtocol):
        """新しいWebSocket接続を登録"""
        self.connections.add(websocket)
        logger.info(f"WebSocket connection registered. Total: {len(self.connections)}")
        
    async def unregister(self, websocket: WebSocketServerProtocol):
        """WebSocket接続を削除"""
        self.connections.discard(websocket)
        logger.info(f"WebSocket connection unregistered. Total: {len(self.connections)}")
        
    async def broadcast(self, message: dict):
        """全ての接続にメッセージをブロードキャスト"""
        if not self.connections:
            return
            
        message_str = json.dumps(message, ensure_ascii=False)
        disconnected = set()
        
        for websocket in self.connections:
            try:
                await websocket.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending message to websocket: {e}")
                disconnected.add(websocket)
                
        # 切断された接続を削除
        for websocket in disconnected:
            self.connections.discard(websocket)
            
    async def send_price_update(self, symbol: str, price: float, change: float):
        """価格更新をブロードキャスト"""
        message = {
            "type": "price_update",
            "data": {
                "symbol": symbol,
                "price": price,
                "change": change,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.broadcast(message)
        
    async def send_pair_update(self, pair_id: int, z_score: float, status: str):
        """ペア状態更新をブロードキャスト"""
        message = {
            "type": "pair_update",
            "data": {
                "pair_id": pair_id,
                "z_score": z_score,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.broadcast(message)
        
    async def send_alert(self, alert_data: dict):
        """アラートをブロードキャスト"""
        message = {
            "type": "alert",
            "data": {
                **alert_data,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self.broadcast(message)
        
    async def start_monitoring(self):
        """リアルタイム監視を開始"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        logger.info("Starting real-time monitoring...")
        
        while self.monitoring_active:
            try:
                await self.monitor_pairs()
                await asyncio.sleep(30)  # 30秒間隔で監視
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # エラー時は1分待機
                
    async def stop_monitoring(self):
        """リアルタイム監視を停止"""
        self.monitoring_active = False
        logger.info("Stopping real-time monitoring...")
        
    async def monitor_pairs(self):
        """ペアの監視とアラート生成"""
        db = next(get_db())
        try:
            # アクティブなペアを取得
            active_pairs = db.query(Pair).filter(Pair.enabled == True).all()
            
            for pair in active_pairs:
                try:
                    # 最新価格を取得
                    price_a = await self.jquants_client.get_latest_price(pair.symbol_a)
                    price_b = await self.jquants_client.get_latest_price(pair.symbol_b)
                    
                    if price_a and price_b:
                        # Z-Scoreを計算
                        z_score = await self.calculate_z_score(pair, price_a, price_b)
                        
                        # ペア状態を更新
                        await self.update_pair_state(db, pair, z_score, price_a, price_b)
                        
                        # アラートをチェック
                        await self.check_alerts(db, pair, z_score)
                        
                        # WebSocketで更新を送信
                        await self.send_pair_update(pair.id, z_score, "active")
                        
                except Exception as e:
                    logger.error(f"Error monitoring pair {pair.id}: {e}")
                    
        finally:
            db.close()
            
    async def calculate_z_score(self, pair: Pair, price_a: float, price_b: float) -> float:
        """Z-Scoreを計算"""
        # 簡単な実装（実際にはより複雑な統計計算が必要）
        spread = price_a - price_b * pair.beta if hasattr(pair, 'beta') else price_a - price_b
        
        # 過去のスプレッドデータから平均と標準偏差を計算
        # ここでは仮の値を使用
        mean_spread = 0.0
        std_spread = 100.0
        
        z_score = (spread - mean_spread) / std_spread if std_spread > 0 else 0.0
        return z_score
        
    async def update_pair_state(self, db: Session, pair: Pair, z_score: float, price_a: float, price_b: float):
        """ペア状態をデータベースに更新"""
        pair_state = db.query(PairState).filter(PairState.pair_id == pair.id).first()
        
        if not pair_state:
            pair_state = PairState(
                pair_id=pair.id,
                z_score=z_score,
                price_a=price_a,
                price_b=price_b,
                spread=price_a - price_b,
                updated_at=datetime.now()
            )
            db.add(pair_state)
        else:
            pair_state.z_score = z_score
            pair_state.price_a = price_a
            pair_state.price_b = price_b
            pair_state.spread = price_a - price_b
            pair_state.updated_at = datetime.now()
            
        db.commit()
        
    async def check_alerts(self, db: Session, pair: Pair, z_score: float):
        """アラート条件をチェックして通知を送信"""
        # アラートルールを取得（簡単な実装）
        entry_threshold = 2.0
        exit_threshold = 0.2
        
        alert_type = None
        message = ""
        
        if abs(z_score) >= entry_threshold:
            if z_score > 0:
                alert_type = "ENTRY_SHORT"
                message = f"Z-Score {z_score:.2f}でショートエントリーシグナル"
            else:
                alert_type = "ENTRY_LONG"
                message = f"Z-Score {z_score:.2f}でロングエントリーシグナル"
        elif abs(z_score) <= exit_threshold:
            alert_type = "EXIT"
            message = f"Z-Score {z_score:.2f}で平均回帰によるエグジット"
            
        if alert_type:
            # アラートをデータベースに保存
            alert = Alert(
                pair_id=pair.id,
                alert_type=alert_type,
                message=message,
                z_score=z_score,
                status="active",
                created_at=datetime.now()
            )
            db.add(alert)
            db.commit()
            
            # WebSocketでアラートを送信
            await self.send_alert({
                "id": alert.id,
                "pair_name": f"{pair.symbol_a}/{pair.symbol_b}",
                "type": alert_type,
                "message": message,
                "z_score": z_score
            })
            
            # 外部通知を送信
            await self.send_external_notification(alert, pair)
            
    async def send_external_notification(self, alert: Alert, pair: Pair):
        """外部通知（Discord、Email等）を送信"""
        try:
            # Discord通知の実装例
            await self.send_discord_notification(alert, pair)
            
            # Email通知の実装例
            await self.send_email_notification(alert, pair)
            
        except Exception as e:
            logger.error(f"Error sending external notification: {e}")
            
    async def send_discord_notification(self, alert: Alert, pair: Pair):
        """Discord通知を送信"""
        # Discord Webhook実装
        # 実際の実装では環境変数からWebhook URLを取得
        pass
        
    async def send_email_notification(self, alert: Alert, pair: Pair):
        """Email通知を送信"""
        # Email送信実装
        # 実際の実装ではSMTPサーバー設定が必要
        pass

# グローバルWebSocketマネージャー
websocket_manager = WebSocketManager()

async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
    """WebSocket接続ハンドラー"""
    await websocket_manager.register(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_websocket_message(websocket, data)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling websocket message: {e}")
                await websocket.send(json.dumps({
                    "type": "error", 
                    "message": str(e)
                }))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await websocket_manager.unregister(websocket)

async def handle_websocket_message(websocket: WebSocketServerProtocol, data: dict):
    """WebSocketメッセージを処理"""
    message_type = data.get("type")
    
    if message_type == "ping":
        await websocket.send(json.dumps({"type": "pong"}))
    elif message_type == "subscribe_pair":
        pair_id = data.get("pair_id")
        # ペア固有の購読処理
        await websocket.send(json.dumps({
            "type": "subscribed",
            "pair_id": pair_id
        }))
    elif message_type == "start_monitoring":
        if not websocket_manager.monitoring_active:
            asyncio.create_task(websocket_manager.start_monitoring())
        await websocket.send(json.dumps({
            "type": "monitoring_started"
        }))
    elif message_type == "stop_monitoring":
        await websocket_manager.stop_monitoring()
        await websocket.send(json.dumps({
            "type": "monitoring_stopped"
        }))

async def start_websocket_server(host: str = "localhost", port: int = 8765):
    """WebSocketサーバーを開始"""
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    server = await websockets.serve(
        websocket_handler,
        host,
        port,
        ping_interval=20,
        ping_timeout=10
    )
    
    # 監視を自動開始
    asyncio.create_task(websocket_manager.start_monitoring())
    
    return server

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        server = await start_websocket_server()
        logger.info("WebSocket server started. Press Ctrl+C to stop.")
        
        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            logger.info("Shutting down WebSocket server...")
            await websocket_manager.stop_monitoring()
            server.close()
            await server.wait_closed()
    
    asyncio.run(main())
