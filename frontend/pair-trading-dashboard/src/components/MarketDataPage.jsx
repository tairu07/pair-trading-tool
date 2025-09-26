import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Database, 
  Search, 
  Filter, 
  Download, 
  RefreshCw,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Calendar
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, CandlestickChart } from 'recharts'

// Mock data
const mockSymbols = [
  { symbol: '7203', name: 'トヨタ自動車', exchange: 'TSE', sector: '輸送用機器', price: 2850, change: 45, changePercent: 1.6, volume: 12500000 },
  { symbol: '7267', name: '本田技研工業', exchange: 'TSE', sector: '輸送用機器', price: 1420, change: -12, changePercent: -0.8, volume: 8900000 },
  { symbol: '8306', name: '三菱UFJフィナンシャル・グループ', exchange: 'TSE', sector: '銀行業', price: 1250, change: 8, changePercent: 0.6, volume: 45600000 },
  { symbol: '8316', name: '三井住友フィナンシャルグループ', exchange: 'TSE', sector: '銀行業', price: 4890, change: -25, changePercent: -0.5, volume: 15200000 },
  { symbol: '6758', name: 'ソニーグループ', exchange: 'TSE', sector: '電気機器', price: 12500, change: 180, changePercent: 1.5, volume: 3400000 },
  { symbol: '6861', name: 'キーエンス', exchange: 'TSE', sector: '電気機器', price: 48900, change: -320, changePercent: -0.6, volume: 890000 },
]

const mockPriceData = [
  { date: '2024-09-20', open: 2800, high: 2870, low: 2790, close: 2850, volume: 12000000 },
  { date: '2024-09-21', open: 2850, high: 2890, low: 2830, close: 2875, volume: 11500000 },
  { date: '2024-09-22', open: 2875, high: 2920, low: 2860, close: 2910, volume: 13200000 },
  { date: '2024-09-23', open: 2910, high: 2950, low: 2895, close: 2935, volume: 14100000 },
  { date: '2024-09-24', open: 2935, high: 2960, low: 2920, close: 2940, volume: 12800000 },
  { date: '2024-09-25', open: 2940, high: 2970, low: 2925, close: 2955, volume: 11900000 },
  { date: '2024-09-26', open: 2955, high: 2980, low: 2940, close: 2850, volume: 12500000 },
]

const mockCorrelationData = [
  { pair: '7203/7267', correlation: 0.78, period: '30日', lastUpdate: '2024-09-26 15:00' },
  { pair: '8306/8316', correlation: 0.85, period: '30日', lastUpdate: '2024-09-26 15:00' },
  { pair: '6758/6861', correlation: 0.62, period: '30日', lastUpdate: '2024-09-26 15:00' },
  { pair: '7203/8306', correlation: 0.45, period: '30日', lastUpdate: '2024-09-26 15:00' },
]

export function MarketDataPage() {
  const [activeTab, setActiveTab] = useState('symbols')
  const [selectedSymbol, setSelectedSymbol] = useState('7203')
  const [searchTerm, setSearchTerm] = useState('')
  const [sectorFilter, setSectorFilter] = useState('all')
  const [isLoading, setIsLoading] = useState(false)

  const filteredSymbols = mockSymbols.filter(symbol => {
    const matchesSearch = symbol.symbol.includes(searchTerm) ||
                         symbol.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSector = sectorFilter === 'all' || symbol.sector === sectorFilter
    return matchesSearch && matchesSector
  })

  const selectedSymbolData = mockSymbols.find(s => s.symbol === selectedSymbol)

  const handleRefresh = () => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }

  const getChangeColor = (change) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600'
  }

  const getChangeBadge = (change) => {
    return change >= 0 ? 'default' : 'destructive'
  }

  const sectors = [...new Set(mockSymbols.map(s => s.sector))]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">マーケットデータ</h1>
          <p className="text-muted-foreground">
            株価データ、相関分析、市場統計の確認
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={isLoading} className="gap-2">
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          データ更新
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="symbols">銘柄一覧</TabsTrigger>
          <TabsTrigger value="prices">価格チャート</TabsTrigger>
          <TabsTrigger value="correlation">相関分析</TabsTrigger>
          <TabsTrigger value="statistics">市場統計</TabsTrigger>
        </TabsList>

        {/* Symbols Tab */}
        <TabsContent value="symbols" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                    <Input
                      placeholder="銘柄コード、銘柄名で検索..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={sectorFilter} onValueChange={setSectorFilter}>
                  <SelectTrigger className="w-[200px]">
                    <Filter className="w-4 h-4 mr-2" />
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">すべてのセクター</SelectItem>
                    {sectors.map(sector => (
                      <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Symbols Table */}
          <Card>
            <CardHeader>
              <CardTitle>銘柄一覧</CardTitle>
              <CardDescription>現在監視中の銘柄とリアルタイム価格</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredSymbols.map((symbol) => (
                  <div key={symbol.symbol} className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div>
                        <div className="font-medium text-lg">{symbol.symbol}</div>
                        <div className="text-sm text-muted-foreground">{symbol.name}</div>
                      </div>
                      <Badge variant="outline">{symbol.sector}</Badge>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-xl font-bold">{symbol.price.toLocaleString()}</div>
                      <div className={`text-sm flex items-center ${getChangeColor(symbol.change)}`}>
                        {symbol.change >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                        {symbol.change > 0 ? '+' : ''}{symbol.change} ({symbol.changePercent > 0 ? '+' : ''}{symbol.changePercent}%)
                      </div>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      <div>出来高</div>
                      <div>{(symbol.volume / 1000000).toFixed(1)}M</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Prices Tab */}
        <TabsContent value="prices" className="space-y-6">
          <div className="flex items-center space-x-4">
            <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {mockSymbols.map(symbol => (
                  <SelectItem key={symbol.symbol} value={symbol.symbol}>
                    {symbol.symbol} - {symbol.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              データエクスポート
            </Button>
          </div>

          {selectedSymbolData && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Price Info Cards */}
              <Card>
                <CardContent className="pt-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{selectedSymbolData.price.toLocaleString()}</div>
                    <div className="text-sm text-muted-foreground">現在価格</div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="text-center">
                    <div className={`text-2xl font-bold ${getChangeColor(selectedSymbolData.change)}`}>
                      {selectedSymbolData.change > 0 ? '+' : ''}{selectedSymbolData.change}
                    </div>
                    <div className="text-sm text-muted-foreground">前日比</div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="text-center">
                    <div className={`text-2xl font-bold ${getChangeColor(selectedSymbolData.changePercent)}`}>
                      {selectedSymbolData.changePercent > 0 ? '+' : ''}{selectedSymbolData.changePercent}%
                    </div>
                    <div className="text-sm text-muted-foreground">騰落率</div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{(selectedSymbolData.volume / 1000000).toFixed(1)}M</div>
                    <div className="text-sm text-muted-foreground">出来高</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Price Chart */}
          <Card>
            <CardHeader>
              <CardTitle>価格チャート - {selectedSymbolData?.name}</CardTitle>
              <CardDescription>過去7日間の価格推移</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={mockPriceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [value.toLocaleString(), name === 'close' ? '終値' : name]}
                    labelFormatter={(label) => `日付: ${label}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="close" 
                    stroke="hsl(var(--primary))" 
                    strokeWidth={2}
                    dot={{ fill: 'hsl(var(--primary))' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Correlation Tab */}
        <TabsContent value="correlation" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>ペア相関分析</CardTitle>
              <CardDescription>銘柄間の相関係数とその推移</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockCorrelationData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <div className="font-medium text-lg">{item.pair}</div>
                      <div className="text-sm text-muted-foreground">期間: {item.period}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">{item.correlation.toFixed(3)}</div>
                      <div className="text-xs text-muted-foreground">相関係数</div>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      <div>最終更新</div>
                      <div>{item.lastUpdate}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Statistics Tab */}
        <TabsContent value="statistics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">監視銘柄数</p>
                    <p className="text-2xl font-bold">{mockSymbols.length}</p>
                  </div>
                  <Database className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">上昇銘柄</p>
                    <p className="text-2xl font-bold text-green-600">
                      {mockSymbols.filter(s => s.change > 0).length}
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">下落銘柄</p>
                    <p className="text-2xl font-bold text-red-600">
                      {mockSymbols.filter(s => s.change < 0).length}
                    </p>
                  </div>
                  <TrendingDown className="w-8 h-8 text-red-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">総出来高</p>
                    <p className="text-2xl font-bold">
                      {(mockSymbols.reduce((sum, s) => sum + s.volume, 0) / 1000000).toFixed(0)}M
                    </p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>セクター別分布</CardTitle>
              <CardDescription>監視銘柄のセクター別内訳</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {sectors.map(sector => {
                  const count = mockSymbols.filter(s => s.sector === sector).length
                  const percentage = (count / mockSymbols.length * 100).toFixed(1)
                  return (
                    <div key={sector} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{sector}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-secondary rounded-full h-2">
                          <div 
                            className="bg-primary h-2 rounded-full" 
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-muted-foreground w-12 text-right">
                          {count}銘柄
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
