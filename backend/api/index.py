"""
Vercel用のエントリーポイント
"""
import os
import sys

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel用のハンドラー
def handler(request, response):
    return app(request, response)

# 直接実行時
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
