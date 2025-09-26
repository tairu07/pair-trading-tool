// API設定
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://your-project.vercel.app' // 本番環境のURL（デプロイ後に更新）
  : 'http://localhost:8000'

export const API_ENDPOINTS = {
  BASE_URL: API_BASE_URL,
  HEALTH: `${API_BASE_URL}/health`,
  PAIRS: `${API_BASE_URL}/api/v1/pairs`,
  BACKTEST: `${API_BASE_URL}/api/v1/backtest`,
  ALERTS: `${API_BASE_URL}/api/v1/alerts`,
  MARKET_DATA: `${API_BASE_URL}/api/v1/market-data`,
  SYSTEM: `${API_BASE_URL}/api/system`
}

// WebSocket設定
export const WS_URL = import.meta.env.PROD
  ? 'wss://your-project.vercel.app/ws' // 本番環境のWebSocket URL
  : 'ws://localhost:8000/ws'

export default API_ENDPOINTS
