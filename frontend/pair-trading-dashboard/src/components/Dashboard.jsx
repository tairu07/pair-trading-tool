import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Bell, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

// Mock data for demonstration
const mockPairs = [
  { id: 1, symbolA: '7203', symbolB: '7267', name: 'トヨタ/ホンダ', zScore: 2.34, correlation: 0.78, beta: 1.12, enabled: true },
  { id: 2, symbolA: '8306', symbolB: '8316', name: 'MUFG/SMFG', zScore: -1.87, correlation: 0.85, beta: 0.94, enabled: true },
  { id: 3, symbolA: '6758', symbolB: '6861', name: 'ソニー/キーエンス', zScore: 0.45, correlation: 0.62, beta: 1.23, enabled: false },
  { id: 4, symbolA: '9983', symbolB: '3382', name: 'ファーストリテイリング/セブン&アイ', zScore: -2.12, correlation: 0.71, beta: 0.87, enabled: true },
]

const mockAlerts = [
  { id: 1, pair: 'トヨタ/ホンダ', type: 'ENTRY_SHORT', zScore: 2.34, time: '10:30', status: 'active' },
  { id: 2, pair: 'MUFG/SMFG', type: 'ENTRY_LONG', zScore: -1.87, time: '09:45', status: 'triggered' },
  { id: 3, pair: 'ファーストリテイリング/セブン&アイ', type: 'EXIT', zScore: -0.15, time: '14:20', status: 'completed' },
]

const mockPerformanceData = [
  { date: '2024-01', pnl: 2.3, trades: 12 },
  { date: '2024-02', pnl: -0.8, trades: 8 },
  { date: '2024-03', pnl: 4.1, trades: 15 },
  { date: '2024-04', pnl: 1.9, trades: 10 },
  { date: '2024-05', pnl: 3.2, trades: 14 },
  { date: '2024-06', pnl: -1.2, trades: 6 },
]

export function Dashboard() {
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  const handleRefresh = () => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      setLastUpdate(new Date())
    }, 1000)
  }

  const activePairs = mockPairs.filter(pair => pair.enabled).length
  const totalAlerts = mockAlerts.length
  const activeAlerts = mockAlerts.filter(alert => alert.status === 'active').length
  const totalPnL = mockPerformanceData.reduce((sum, data) => sum + data.pnl, 0)

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">ダッシュボード</h1>
          <p className="text-muted-foreground">
            最終更新: {lastUpdate.toLocaleTimeString('ja-JP')}
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={isLoading} className="gap-2">
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          更新
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">アクティブペア</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activePairs}</div>
            <p className="text-xs text-muted-foreground">
              全{mockPairs.length}ペア中
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">アラート</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeAlerts}</div>
            <p className="text-xs text-muted-foreground">
              アクティブ / 全{totalAlerts}件
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">累積PnL</CardTitle>
            {totalPnL >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalPnL > 0 ? '+' : ''}{totalPnL.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              過去6ヶ月
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">取引回数</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockPerformanceData.reduce((sum, data) => sum + data.trades, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              過去6ヶ月
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>パフォーマンス推移</CardTitle>
            <CardDescription>月次PnL推移</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'PnL']}
                  labelFormatter={(label) => `期間: ${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="pnl" 
                  stroke="hsl(var(--primary))" 
                  strokeWidth={2}
                  dot={{ fill: 'hsl(var(--primary))' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Active Pairs */}
        <Card>
          <CardHeader>
            <CardTitle>アクティブペア</CardTitle>
            <CardDescription>現在監視中のペア一覧</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockPairs.filter(pair => pair.enabled).map((pair) => (
                <div key={pair.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{pair.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {pair.symbolA} / {pair.symbolB}
                    </div>
                  </div>
                  <div className="text-right space-y-1">
                    <Badge 
                      variant={Math.abs(pair.zScore) >= 2 ? "destructive" : "secondary"}
                      className="text-xs"
                    >
                      Z: {pair.zScore.toFixed(2)}
                    </Badge>
                    <div className="text-xs text-muted-foreground">
                      ρ: {pair.correlation.toFixed(2)} | β: {pair.beta.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>最近のアラート</CardTitle>
          <CardDescription>直近のアラート履歴</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockAlerts.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  {alert.status === 'active' && <AlertTriangle className="w-4 h-4 text-orange-500" />}
                  {alert.status === 'triggered' && <Clock className="w-4 h-4 text-blue-500" />}
                  {alert.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-500" />}
                  <div>
                    <div className="font-medium">{alert.pair}</div>
                    <div className="text-sm text-muted-foreground">{alert.type}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">Z: {alert.zScore.toFixed(2)}</div>
                  <div className="text-xs text-muted-foreground">{alert.time}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
