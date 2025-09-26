# ペアトレード管理ツール

サヤ取り（ペアトレード）の探索→監視→アラート→簡易バックテストを一気通貫で提供するツールです。

## 概要

このツールは、J-Quantsを価格データソースとして、ペアトレードの全工程をサポートします：

- **ペア登録・管理**: 手動でのペア入力と管理
- **リアルタイム監視**: z乖離、相関、β値の継続的な監視
- **アラート機能**: Discord/Slack/LINEへの即時通知
- **バックテスト**: 選択期間での戦略検証
- **ダッシュボード**: 直感的なWebインターフェース

## 技術スタック

- **Frontend**: Next.js (App Router)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + DuckDB
- **Queue**: Redis (将来拡張)
- **通知**: Discord Webhook
- **価格源**: J-Quants API

## プロジェクト構造

```
pair-trading-tool/
├── backend/          # FastAPI バックエンド
├── frontend/         # Next.js フロントエンド
├── database/         # データベーススキーマとマイグレーション
├── docker/           # Docker設定ファイル
├── docs/             # ドキュメント
└── scripts/          # ユーティリティスクリプト
```

## 開発フェーズ

### Phase 1 (MVP)
- [x] プロジェクト構造とセットアップ
- [ ] データベース設計
- [ ] バックエンドAPI基盤
- [ ] フロントエンドダッシュボード
- [ ] リアルタイム監視とアラート

### Phase 2 (拡張)
- [ ] 自動ペア探索
- [ ] 高度なバックテスト機能
- [ ] リスク管理機能

## セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/tairu07/pair-trading-tool.git
cd pair-trading-tool

# Docker環境の起動
docker-compose up -d

# 開発サーバーの起動
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

## ライセンス

MIT License
