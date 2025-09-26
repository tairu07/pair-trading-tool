import asyncio
import aiohttp
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import os
from models import Alert, Pair

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        # Discord設定
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        # Email設定
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', self.email_user)
        
        # 通知設定
        self.notification_channels = {
            'discord': self.discord_webhook_url is not None,
            'email': self.email_user is not None and self.email_password is not None
        }
        
        logger.info(f"Notification channels available: {self.notification_channels}")
        
    async def send_alert_notification(self, alert: Alert, pair: Pair, channels: List[str] = None):
        """アラート通知を送信"""
        if channels is None:
            channels = ['discord', 'email']
            
        tasks = []
        
        if 'discord' in channels and self.notification_channels['discord']:
            tasks.append(self.send_discord_alert(alert, pair))
            
        if 'email' in channels and self.notification_channels['email']:
            tasks.append(self.send_email_alert(alert, pair))
            
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error sending notification via {channels[i]}: {result}")
                else:
                    logger.info(f"Notification sent successfully via {channels[i]}")
        else:
            logger.warning("No notification channels configured")
            
    async def send_discord_alert(self, alert: Alert, pair: Pair):
        """Discord Webhookでアラートを送信"""
        if not self.discord_webhook_url:
            raise ValueError("Discord webhook URL not configured")
            
        # アラートタイプに応じた色とアイコンを設定
        color_map = {
            'ENTRY_LONG': 0x00ff00,    # 緑
            'ENTRY_SHORT': 0xff0000,   # 赤
            'EXIT': 0x0099ff,          # 青
            'STOP_LOSS': 0xff6600      # オレンジ
        }
        
        emoji_map = {
            'ENTRY_LONG': '📈',
            'ENTRY_SHORT': '📉',
            'EXIT': '🔄',
            'STOP_LOSS': '⚠️'
        }
        
        color = color_map.get(alert.alert_type, 0x808080)
        emoji = emoji_map.get(alert.alert_type, '🔔')
        
        # Discordエンベッドメッセージを作成
        embed = {
            "title": f"{emoji} ペアトレーディングアラート",
            "description": alert.message,
            "color": color,
            "fields": [
                {
                    "name": "ペア",
                    "value": f"{pair.symbol_a} / {pair.symbol_b}",
                    "inline": True
                },
                {
                    "name": "Z-Score",
                    "value": f"{alert.z_score:.2f}",
                    "inline": True
                },
                {
                    "name": "アラートタイプ",
                    "value": alert.alert_type,
                    "inline": True
                }
            ],
            "timestamp": alert.created_at.isoformat(),
            "footer": {
                "text": "Pair Trading Tool"
            }
        }
        
        payload = {
            "embeds": [embed],
            "username": "Pair Trading Bot"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.discord_webhook_url, json=payload) as response:
                if response.status != 204:
                    error_text = await response.text()
                    raise Exception(f"Discord webhook failed: {response.status} - {error_text}")
                    
    async def send_email_alert(self, alert: Alert, pair: Pair):
        """Emailでアラートを送信"""
        if not self.email_user or not self.email_password:
            raise ValueError("Email credentials not configured")
            
        # メール受信者（環境変数から取得、デフォルトは送信者と同じ）
        recipients = os.getenv('EMAIL_RECIPIENTS', self.email_user).split(',')
        
        # メール内容を作成
        subject = f"[Pair Trading Alert] {alert.alert_type} - {pair.symbol_a}/{pair.symbol_b}"
        
        html_body = self.create_email_html(alert, pair)
        text_body = self.create_email_text(alert, pair)
        
        # MIMEメッセージを作成
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = ', '.join(recipients)
        
        # テキストとHTMLパートを追加
        text_part = MIMEText(text_body, 'plain', 'utf-8')
        html_part = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # 非同期でメール送信
        await self.send_email_async(msg, recipients)
        
    def create_email_html(self, alert: Alert, pair: Pair) -> str:
        """HTMLメール本文を作成"""
        color_map = {
            'ENTRY_LONG': '#28a745',
            'ENTRY_SHORT': '#dc3545',
            'EXIT': '#007bff',
            'STOP_LOSS': '#fd7e14'
        }
        
        color = color_map.get(alert.alert_type, '#6c757d')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Pair Trading Alert</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔔 ペアトレーディングアラート</h1>
                </div>
                <div style="padding: 20px;">
                    <h2 style="color: #333; margin-top: 0;">{alert.message}</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">ペア:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{pair.symbol_a} / {pair.symbol_b}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Z-Score:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; color: {color}; font-weight: bold;">{alert.z_score:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">アラートタイプ:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.alert_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">発生時刻:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                    </table>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 20px;">
                        <p style="margin: 0; color: #6c757d; font-size: 14px;">
                            このアラートはPair Trading Toolによって自動生成されました。<br>
                            詳細な分析はダッシュボードでご確認ください。
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
    def create_email_text(self, alert: Alert, pair: Pair) -> str:
        """テキストメール本文を作成"""
        return f"""
ペアトレーディングアラート

{alert.message}

詳細情報:
- ペア: {pair.symbol_a} / {pair.symbol_b}
- Z-Score: {alert.z_score:.2f}
- アラートタイプ: {alert.alert_type}
- 発生時刻: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}

このアラートはPair Trading Toolによって自動生成されました。
詳細な分析はダッシュボードでご確認ください。
        """
        
    async def send_email_async(self, msg: MIMEMultipart, recipients: List[str]):
        """非同期でメールを送信"""
        def send_email():
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                    server.send_message(msg, to_addrs=recipients)
                return True
            except Exception as e:
                raise Exception(f"Failed to send email: {e}")
                
        # 別スレッドでメール送信を実行
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_email)
        
    async def send_backtest_completion_notification(self, job_id: int, job_name: str, results: Dict):
        """バックテスト完了通知を送信"""
        total_pnl = results.get('total_pnl', 0)
        total_trades = results.get('total_trades', 0)
        win_rate = results.get('win_rate', 0)
        
        # Discord通知
        if self.notification_channels['discord']:
            embed = {
                "title": "📊 バックテスト完了",
                "description": f"バックテスト '{job_name}' が完了しました",
                "color": 0x00ff00 if total_pnl > 0 else 0xff0000,
                "fields": [
                    {
                        "name": "総PnL",
                        "value": f"{total_pnl:+.2f}%",
                        "inline": True
                    },
                    {
                        "name": "取引回数",
                        "value": str(total_trades),
                        "inline": True
                    },
                    {
                        "name": "勝率",
                        "value": f"{win_rate:.1%}",
                        "inline": True
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "Pair Trading Tool"
                }
            }
            
            payload = {
                "embeds": [embed],
                "username": "Pair Trading Bot"
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.discord_webhook_url, json=payload) as response:
                        if response.status == 204:
                            logger.info("Backtest completion notification sent to Discord")
            except Exception as e:
                logger.error(f"Failed to send Discord backtest notification: {e}")
                
    async def test_notifications(self):
        """通知システムのテスト"""
        logger.info("Testing notification systems...")
        
        # テスト用のダミーデータ
        class DummyAlert:
            def __init__(self):
                self.alert_type = 'ENTRY_LONG'
                self.message = 'テスト用アラート - システムが正常に動作しています'
                self.z_score = 2.15
                self.created_at = datetime.now()
                
        class DummyPair:
            def __init__(self):
                self.symbol_a = '7203'
                self.symbol_b = '7267'
                
        dummy_alert = DummyAlert()
        dummy_pair = DummyPair()
        
        try:
            await self.send_alert_notification(dummy_alert, dummy_pair)
            logger.info("Notification test completed successfully")
        except Exception as e:
            logger.error(f"Notification test failed: {e}")

# グローバル通知マネージャー
notification_manager = NotificationManager()

async def send_alert_notification(alert: Alert, pair: Pair, channels: List[str] = None):
    """アラート通知を送信（外部インターフェース）"""
    await notification_manager.send_alert_notification(alert, pair, channels)
    
async def test_notifications():
    """通知システムのテスト（外部インターフェース）"""
    await notification_manager.test_notifications()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        await test_notifications()
    
    asyncio.run(main())
