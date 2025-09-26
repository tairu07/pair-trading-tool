"""
Working FastAPI application for Vercel deployment
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import json

# Create FastAPI application
app = FastAPI(
    title="Pair Trading Tool API",
    description="API for managing pair trading strategies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Pair(BaseModel):
    id: str
    symbol_a: str
    symbol_b: str
    name: str
    status: str
    z_score: Optional[float] = None
    created_at: str

class PairCreate(BaseModel):
    symbol_a: str
    symbol_b: str
    name: str

# Mock data
mock_pairs = [
    {
        "id": "1",
        "symbol_a": "7203",
        "symbol_b": "7267", 
        "name": "トヨタ/ホンダ",
        "status": "active",
        "z_score": 1.2,
        "created_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "2",
        "symbol_a": "8306",
        "symbol_b": "8316",
        "name": "MUFG/SMFG",
        "status": "active", 
        "z_score": -0.8,
        "created_at": "2024-01-02T00:00:00Z"
    },
    {
        "id": "3",
        "symbol_a": "6758",
        "symbol_b": "6861",
        "name": "ソニー/キーエンス",
        "status": "monitoring",
        "z_score": 2.1,
        "created_at": "2024-01-03T00:00:00Z"
    }
]

# Frontend HTML
frontend_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pair Trading Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { color: #333; margin-bottom: 10px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
        .stat-card .value { font-size: 24px; font-weight: bold; color: #333; }
        .pairs-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .pairs-table { width: 100%; border-collapse: collapse; }
        .pairs-table th, .pairs-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .pairs-table th { background: #f8f9fa; font-weight: 600; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
        .status.active { background: #d4edda; color: #155724; }
        .status.monitoring { background: #fff3cd; color: #856404; }
        .z-score { font-weight: 600; }
        .z-score.positive { color: #dc3545; }
        .z-score.negative { color: #28a745; }
        .z-score.neutral { color: #6c757d; }
        .api-section { margin-top: 30px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .api-links a { display: inline-block; margin-right: 15px; padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 10px; }
        .api-links a:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Pair Trading Tool</h1>
            <p>ペアトレーディング戦略の管理・監視ツール</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>アクティブペア</h3>
                <div class="value" id="active-pairs">2</div>
            </div>
            <div class="stat-card">
                <h3>監視中ペア</h3>
                <div class="value" id="monitoring-pairs">1</div>
            </div>
            <div class="stat-card">
                <h3>総ペア数</h3>
                <div class="value" id="total-pairs">3</div>
            </div>
            <div class="stat-card">
                <h3>システム状態</h3>
                <div class="value" style="color: #28a745;">稼働中</div>
            </div>
        </div>
        
        <div class="pairs-section">
            <h2>ペア一覧</h2>
            <table class="pairs-table">
                <thead>
                    <tr>
                        <th>ペア名</th>
                        <th>銘柄A</th>
                        <th>銘柄B</th>
                        <th>Z-Score</th>
                        <th>ステータス</th>
                        <th>作成日</th>
                    </tr>
                </thead>
                <tbody id="pairs-tbody">
                    <!-- データはJavaScriptで動的に挿入 -->
                </tbody>
            </table>
        </div>
        
        <div class="api-section">
            <h2>API エンドポイント</h2>
            <div class="api-links">
                <a href="/api/v1/pairs" target="_blank">ペア一覧 API</a>
                <a href="/health" target="_blank">ヘルスチェック</a>
                <a href="/docs" target="_blank">API ドキュメント</a>
            </div>
        </div>
    </div>

    <script>
        // ペアデータを取得して表示
        async function loadPairs() {
            try {
                const response = await fetch('/api/v1/pairs');
                const data = await response.json();
                const tbody = document.getElementById('pairs-tbody');
                
                tbody.innerHTML = data.pairs.map(pair => `
                    <tr>
                        <td><strong>${pair.name}</strong></td>
                        <td>${pair.symbol_a}</td>
                        <td>${pair.symbol_b}</td>
                        <td class="z-score ${pair.z_score > 0 ? 'positive' : pair.z_score < 0 ? 'negative' : 'neutral'}">
                            ${pair.z_score ? pair.z_score.toFixed(2) : 'N/A'}
                        </td>
                        <td><span class="status ${pair.status}">${pair.status === 'active' ? 'アクティブ' : '監視中'}</span></td>
                        <td>${new Date(pair.created_at).toLocaleDateString('ja-JP')}</td>
                    </tr>
                `).join('');
                
                // 統計を更新
                const activePairs = data.pairs.filter(p => p.status === 'active').length;
                const monitoringPairs = data.pairs.filter(p => p.status === 'monitoring').length;
                
                document.getElementById('active-pairs').textContent = activePairs;
                document.getElementById('monitoring-pairs').textContent = monitoringPairs;
                document.getElementById('total-pairs').textContent = data.pairs.length;
                
            } catch (error) {
                console.error('ペアデータの取得に失敗:', error);
                document.getElementById('pairs-tbody').innerHTML = '<tr><td colspan="6">データの取得に失敗しました</td></tr>';
            }
        }
        
        // ページ読み込み時にデータを取得
        loadPairs();
        
        // 30秒ごとにデータを更新
        setInterval(loadPairs, 30000);
    </script>
</body>
</html>
"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with dashboard"""
    return frontend_html

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Pair Trading Tool API is running"}

@app.get("/api/v1/pairs")
async def get_pairs():
    """Get all pairs"""
    return {"pairs": mock_pairs, "total": len(mock_pairs)}

@app.get("/api/v1/pairs/{pair_id}")
async def get_pair(pair_id: str):
    """Get specific pair"""
    pair = next((p for p in mock_pairs if p["id"] == pair_id), None)
    if not pair:
        raise HTTPException(status_code=404, detail="Pair not found")
    return pair

@app.post("/api/v1/pairs")
async def create_pair(pair: PairCreate):
    """Create new pair"""
    new_pair = {
        "id": str(len(mock_pairs) + 1),
        "symbol_a": pair.symbol_a,
        "symbol_b": pair.symbol_b,
        "name": pair.name,
        "status": "active",
        "z_score": 0.0,
        "created_at": "2024-01-01T00:00:00Z"
    }
    mock_pairs.append(new_pair)
    return new_pair

@app.get("/api/v1/status")
async def api_status():
    """API status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "environment": os.getenv("VERCEL_ENV", "development"),
        "pairs_count": len(mock_pairs)
    }

# Vercel handler
def handler(request, response):
    return app(request, response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
