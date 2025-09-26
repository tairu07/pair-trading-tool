import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Play, 
  Pause, 
  Square, 
  Download, 
  Settings, 
  TrendingUp,
  TrendingDown,
  BarChart3,
  Clock,
  Target,
  AlertCircle
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

// Mock data
const mockBacktestJobs = [
  {
    id: 1,
    name: 'トヨタ/ホンダ 基本戦略',
    status: 'completed',
    progress: 100,
    createdAt: '2024-09-25 14:30',
    completedAt: '2024-09-25 14:35',
    params: {
      symbolA: '7203',
      symbolB: '7267',
      startDate: '2024-01-01',
      endDate: '2024-09-25',
      entryZ: 2.0,
      exitZ: 0.2
    },
    results: {
      totalTrades: 24,
      winRate: 0.625,
      totalPnL: 8.4,
      maxDrawdown: -2.1,
      sharpeRatio: 1.34
    }
  },
  {
    id: 2,
    name: 'MUFG/SMFG 保守戦略',
    status: 'running',
    progress: 67,
    createdAt: '2024-09-26 09:15',
    params: {
      symbolA: '8306',
      symbolB: '8316',
      startDate: '2024-01-01',
      endDate: '2024-09-26',
      entryZ: 2.5,
      exitZ: 0.1
    }
  },
  {
    id: 3,
    name: 'ソニー/キーエンス アグレッシブ',
    status: 'failed',
    progress: 0,
    createdAt: '2024-09-24 16:45',
    error: 'データ取得エラー'
  }
]

const mockEquityCurve = [
  { date: '2024-01', pnl: 0 },
  { date: '2024-02', pnl: 1.2 },
  { date: '2024-03', pnl: 0.8 },
  { date: '2024-04', pnl: 2.1 },
  { date: '2024-05', pnl: 3.4 },
  { date: '2024-06', pnl: 2.9 },
  { date: '2024-07', pnl: 4.2 },
  { date: '2024-08', pnl: 5.1 },
  { date: '2024-09', pnl: 8.4 }
]

const mockTradeDistribution = [
  { range: '-5% to -3%', count: 2 },
  { range: '-3% to -1%', count: 4 },
  { range: '-1% to 1%', count: 8 },
  { range: '1% to 3%', count: 7 },
  { range: '3% to 5%', count: 3 }
]

export function BacktestPage() {
  const [activeTab, setActiveTab] = useState('create')
  const [selectedJob, setSelectedJob] = useState(mockBacktestJobs[0])
  const [formData, setFormData] = useState({
    name: '',
    symbolA: '',
    symbolB: '',
    startDate: '2024-01-01',
    endDate: '2024-09-26',
    entryZ: '2.0',
    exitZ: '0.2',
    stopZ: '3.5',
    maxHoldDays: '30',
    lookback: '200',
    feeBps: '1.0',
    slipBps: '1.0'
  })

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleRunBacktest = () => {
    console.log('Running backtest with params:', formData)
    // Here you would call the API to start the backtest
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'running': return 'text-blue-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed': return 'default'
      case 'running': return 'secondary'
      case 'failed': return 'destructive'
      default: return 'outline'
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">バックテスト</h1>
        <p className="text-muted-foreground">
          ペアトレーディング戦略の過去データでの検証
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="create">新規作成</TabsTrigger>
          <TabsTrigger value="jobs">実行履歴</TabsTrigger>
          <TabsTrigger value="results">結果分析</TabsTrigger>
        </TabsList>

        {/* Create Backtest Tab */}
        <TabsContent value="create" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>バックテスト設定</CardTitle>
              <CardDescription>
                戦略パラメータを設定してバックテストを実行します
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Settings */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">基本設定</h3>
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="name">バックテスト名</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="例: トヨタ/ホンダ 基本戦略"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="symbolA">銘柄A</Label>
                        <Input
                          id="symbolA"
                          value={formData.symbolA}
                          onChange={(e) => handleInputChange('symbolA', e.target.value)}
                          placeholder="7203"
                        />
                      </div>
                      <div>
                        <Label htmlFor="symbolB">銘柄B</Label>
                        <Input
                          id="symbolB"
                          value={formData.symbolB}
                          onChange={(e) => handleInputChange('symbolB', e.target.value)}
                          placeholder="7267"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="startDate">開始日</Label>
                        <Input
                          id="startDate"
                          type="date"
                          value={formData.startDate}
                          onChange={(e) => handleInputChange('startDate', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label htmlFor="endDate">終了日</Label>
                        <Input
                          id="endDate"
                          type="date"
                          value={formData.endDate}
                          onChange={(e) => handleInputChange('endDate', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Strategy Parameters */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">戦略パラメータ</h3>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="entryZ">エントリーZ値</Label>
                        <Input
                          id="entryZ"
                          type="number"
                          step="0.1"
                          value={formData.entryZ}
                          onChange={(e) => handleInputChange('entryZ', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label htmlFor="exitZ">エグジットZ値</Label>
                        <Input
                          id="exitZ"
                          type="number"
                          step="0.1"
                          value={formData.exitZ}
                          onChange={(e) => handleInputChange('exitZ', e.target.value)}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="stopZ">ストップロスZ値</Label>
                        <Input
                          id="stopZ"
                          type="number"
                          step="0.1"
                          value={formData.stopZ}
                          onChange={(e) => handleInputChange('stopZ', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label htmlFor="maxHoldDays">最大保有日数</Label>
                        <Input
                          id="maxHoldDays"
                          type="number"
                          value={formData.maxHoldDays}
                          onChange={(e) => handleInputChange('maxHoldDays', e.target.value)}
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="lookback">ルックバック期間</Label>
                      <Input
                        id="lookback"
                        type="number"
                        value={formData.lookback}
                        onChange={(e) => handleInputChange('lookback', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <Button variant="outline">
                  <Settings className="w-4 h-4 mr-2" />
                  詳細設定
                </Button>
                <Button onClick={handleRunBacktest}>
                  <Play className="w-4 h-4 mr-2" />
                  バックテスト実行
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Jobs Tab */}
        <TabsContent value="jobs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>実行履歴</CardTitle>
              <CardDescription>
                過去に実行したバックテストの一覧
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockBacktestJobs.map((job) => (
                  <div key={job.id} className="border rounded-lg p-4 hover:bg-accent/50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium">{job.name}</h3>
                          <Badge variant={getStatusBadge(job.status)}>
                            {job.status === 'completed' && '完了'}
                            {job.status === 'running' && '実行中'}
                            {job.status === 'failed' && '失敗'}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {job.params && `${job.params.symbolA}/${job.params.symbolB} | ${job.params.startDate} - ${job.params.endDate}`}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          作成: {job.createdAt}
                          {job.completedAt && ` | 完了: ${job.completedAt}`}
                          {job.error && ` | エラー: ${job.error}`}
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {job.status === 'running' && (
                          <div className="w-24">
                            <Progress value={job.progress} />
                          </div>
                        )}
                        {job.results && (
                          <div className="text-right text-sm">
                            <div className={`font-medium ${job.results.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {job.results.totalPnL > 0 ? '+' : ''}{job.results.totalPnL}%
                            </div>
                            <div className="text-muted-foreground">
                              {job.results.totalTrades}取引
                            </div>
                          </div>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedJob(job)
                            setActiveTab('results')
                          }}
                          disabled={job.status !== 'completed'}
                        >
                          詳細
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          {selectedJob && selectedJob.results && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">総PnL</p>
                        <p className={`text-2xl font-bold ${selectedJob.results.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {selectedJob.results.totalPnL > 0 ? '+' : ''}{selectedJob.results.totalPnL}%
                        </p>
                      </div>
                      {selectedJob.results.totalPnL >= 0 ? (
                        <TrendingUp className="w-8 h-8 text-green-600" />
                      ) : (
                        <TrendingDown className="w-8 h-8 text-red-600" />
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">勝率</p>
                        <p className="text-2xl font-bold">{(selectedJob.results.winRate * 100).toFixed(1)}%</p>
                      </div>
                      <Target className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">取引回数</p>
                        <p className="text-2xl font-bold">{selectedJob.results.totalTrades}</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">シャープレシオ</p>
                        <p className="text-2xl font-bold">{selectedJob.results.sharpeRatio}</p>
                      </div>
                      <TrendingUp className="w-8 h-8 text-orange-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>損益推移</CardTitle>
                    <CardDescription>累積PnLの推移</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={mockEquityCurve}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`${value}%`, 'PnL']} />
                        <Line 
                          type="monotone" 
                          dataKey="pnl" 
                          stroke="hsl(var(--primary))" 
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>取引分布</CardTitle>
                    <CardDescription>PnL別の取引回数分布</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={mockTradeDistribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="range" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="hsl(var(--primary))" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {/* Detailed Stats */}
              <Card>
                <CardHeader>
                  <CardTitle>詳細統計</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-red-600">{selectedJob.results.maxDrawdown}%</div>
                      <div className="text-sm text-muted-foreground">最大ドローダウン</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{selectedJob.results.sharpeRatio}</div>
                      <div className="text-sm text-muted-foreground">シャープレシオ</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{Math.round(selectedJob.results.totalTrades * selectedJob.results.winRate)}</div>
                      <div className="text-sm text-muted-foreground">勝ちトレード</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{selectedJob.results.totalTrades - Math.round(selectedJob.results.totalTrades * selectedJob.results.winRate)}</div>
                      <div className="text-sm text-muted-foreground">負けトレード</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
