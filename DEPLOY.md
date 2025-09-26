# Vercelデプロイガイド

## 前提条件

1. Vercelアカウントの作成
2. Vercel Postgresデータベースの作成
3. 必要な環境変数の準備

## デプロイ手順

### 1. Vercel Postgresデータベースの作成

1. Vercelダッシュボードにログイン
2. 「Storage」→「Create Database」→「Postgres」を選択
3. データベース名を入力（例：`pair-trading-db`）
4. リージョンを選択（推奨：Tokyo）
5. 作成完了後、接続情報をコピー

### 2. 環境変数の設定

Vercelプロジェクト設定で以下の環境変数を設定：

```
DATABASE_URL=postgresql://username:password@host:port/database
J_QUANTS_REFRESH_TOKEN=your_jquants_refresh_token
DISCORD_WEBHOOK_URL=your_discord_webhook_url
SECRET_KEY=your_secret_key_here
DEBUG=false
LOG_LEVEL=INFO
```

### 3. デプロイコマンド

```bash
# Vercel CLIでログイン
vercel login

# プロジェクトをデプロイ
vercel --prod

# または、GitHubと連携してデプロイ
# 1. GitHubリポジトリをVercelに接続
# 2. 自動デプロイが開始される
```

### 4. データベースマイグレーション

デプロイ後、データベースのマイグレーションを実行：

```bash
# ローカルから本番データベースに接続してマイグレーション
DATABASE_URL="your_production_database_url" python backend/init_sample_data.py
```

### 5. 動作確認

- フロントエンド: `https://your-project.vercel.app`
- API: `https://your-project.vercel.app/api/health`
- API Docs: `https://your-project.vercel.app/docs`

## トラブルシューティング

### よくある問題

1. **データベース接続エラー**
   - DATABASE_URLが正しく設定されているか確認
   - Vercel Postgresの接続制限を確認

2. **WebSocket接続エラー**
   - Vercelは長時間のWebSocket接続をサポートしていません
   - リアルタイム機能は制限される可能性があります

3. **ビルドエラー**
   - requirements.txtの依存関係を確認
   - Python バージョンの互換性を確認

### パフォーマンス最適化

1. **データベース接続プール**
   - SQLAlchemyの接続プール設定を最適化

2. **静的ファイル配信**
   - Vercel CDNを活用

3. **API レスポンス時間**
   - 不要なデータベースクエリを削減
   - キャッシュ戦略の実装

## セキュリティ考慮事項

1. **環境変数の管理**
   - 機密情報は必ずVercelの環境変数で管理
   - .envファイルはGitにコミットしない

2. **CORS設定**
   - 本番環境では適切なオリジンのみ許可

3. **API認証**
   - 必要に応じてAPI認証を実装

## 監視とログ

1. **Vercelログ**
   - Vercelダッシュボードでログを確認

2. **エラー監視**
   - Sentryなどのエラー監視サービスの導入を検討

3. **パフォーマンス監視**
   - Vercel Analyticsでパフォーマンスを監視
