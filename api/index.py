from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
pairs_data = [
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

@app.get("/")
def read_root():
    html_content = """
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
                <div class="value">2</div>
            </div>
            <div class="stat-card">
                <h3>監視中ペア</h3>
                <div class="value">1</div>
            </div>
            <div class="stat-card">
                <h3>総ペア数</h3>
                <div class="value">3</div>
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
                <tbody>
                    <tr>
                        <td><strong>トヨタ/ホンダ</strong></td>
                        <td>7203</td>
                        <td>7267</td>
                        <td class="z-score positive">1.20</td>
                        <td><span class="status active">アクティブ</span></td>
                        <td>2024/1/1</td>
                    </tr>
                    <tr>
                        <td><strong>MUFG/SMFG</strong></td>
                        <td>8306</td>
                        <td>8316</td>
                        <td class="z-score negative">-0.80</td>
                        <td><span class="status active">アクティブ</span></td>
                        <td>2024/1/2</td>
                    </tr>
                    <tr>
                        <td><strong>ソニー/キーエンス</strong></td>
                        <td>6758</td>
                        <td>6861</td>
                        <td class="z-score positive">2.10</td>
                        <td><span class="status monitoring">監視中</span></td>
                        <td>2024/1/3</td>
                    </tr>
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
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Pair Trading Tool API is running"}

@app.get("/api/v1/pairs")
def get_pairs():
    return {"pairs": pairs_data, "total": len(pairs_data)}

@app.get("/api/v1/status")
def api_status():
    return {
        "status": "running",
        "version": "1.0.0",
        "pairs_count": len(pairs_data)
    }
