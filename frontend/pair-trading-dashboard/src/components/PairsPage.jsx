import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  TrendingUp,
  TrendingDown,
  Activity,
  Eye
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

// Mock data
const mockPairs = [
  { 
    id: 1, 
    symbolA: '7203', 
    symbolB: '7267', 
    name: 'トヨタ/ホンダ', 
    zScore: 2.34, 
    correlation: 0.78, 
    beta: 1.12, 
    enabled: true,
    description: '自動車セクターのペア',
    createdAt: '2024-01-15',
    priceA: 2850,
    priceB: 1420,
    spread: 145.2
  },
  { 
    id: 2, 
    symbolA: '8306', 
    symbolB: '8316', 
    name: 'MUFG/SMFG', 
    zScore: -1.87, 
    correlation: 0.85, 
    beta: 0.94, 
    enabled: true,
    description: 'メガバンクペア',
    createdAt: '2024-02-01',
    priceA: 1250,
    priceB: 4890,
    spread: -89.3
  },
  { 
    id: 3, 
    symbolA: '6758', 
    symbolB: '6861', 
    name: 'ソニー/キーエンス', 
    zScore: 0.45, 
    correlation: 0.62, 
    beta: 1.23, 
    enabled: false,
    description: 'テクノロジー関連ペア',
    createdAt: '2024-01-20',
    priceA: 12500,
    priceB: 48900,
    spread: 23.1
  },
]

const mockZScoreHistory = [
  { date: '2024-09-20', value: 1.2 },
  { date: '2024-09-21', value: 1.8 },
  { date: '2024-09-22', value: 2.1 },
  { date: '2024-09-23', value: 2.3 },
  { date: '2024-09-24', value: 2.4 },
  { date: '2024-09-25', value: 2.2 },
  { date: '2024-09-26', value: 2.34 },
]

export function PairsPage() {
  const [pairs, setPairs] = useState(mockPairs)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterEnabled, setFilterEnabled] = useState('all')
  const [selectedPair, setSelectedPair] = useState(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false)

  const filteredPairs = pairs.filter(pair => {
    const matchesSearch = pair.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pair.symbolA.includes(searchTerm) ||
                         pair.symbolB.includes(searchTerm)
    const matchesFilter = filterEnabled === 'all' || 
                         (filterEnabled === 'enabled' && pair.enabled) ||
                         (filterEnabled === 'disabled' && !pair.enabled)
    return matchesSearch && matchesFilter
  })

  const handleToggleEnabled = (id) => {
    setPairs(pairs.map(pair => 
      pair.id === id ? { ...pair, enabled: !pair.enabled } : pair
    ))
  }

  const handleDeletePair = (id) => {
    setPairs(pairs.filter(pair => pair.id !== id))
  }

  const getZScoreColor = (zScore) => {
    const abs = Math.abs(zScore)
    if (abs >= 2.5) return 'text-red-600'
    if (abs >= 2.0) return 'text-orange-600'
    if (abs >= 1.5) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getZScoreBadgeVariant = (zScore) => {
    const abs = Math.abs(zScore)
    if (abs >= 2.0) return 'destructive'
    if (abs >= 1.5) return 'secondary'
    return 'outline'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">ペア管理</h1>
          <p className="text-muted-foreground">
            トレーディングペアの作成・管理・監視
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              新規ペア作成
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>新規ペア作成</DialogTitle>
              <DialogDescription>
                新しいトレーディングペアを作成します
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="symbolA">銘柄A</Label>
                  <Input id="symbolA" placeholder="7203" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="symbolB">銘柄B</Label>
                  <Input id="symbolB" placeholder="7267" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">ペア名</Label>
                <Input id="name" placeholder="トヨタ/ホンダ" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">説明</Label>
                <Textarea id="description" placeholder="ペアの説明を入力..." />
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="enabled" />
                <Label htmlFor="enabled">監視を有効にする</Label>
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                キャンセル
              </Button>
              <Button onClick={() => setIsCreateDialogOpen(false)}>
                作成
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="ペア名、銘柄コードで検索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={filterEnabled} onValueChange={setFilterEnabled}>
              <SelectTrigger className="w-[180px]">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">すべて</SelectItem>
                <SelectItem value="enabled">有効のみ</SelectItem>
                <SelectItem value="disabled">無効のみ</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Pairs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPairs.map((pair) => (
          <Card key={pair.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{pair.name}</CardTitle>
                  <CardDescription>{pair.symbolA} / {pair.symbolB}</CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={pair.enabled}
                    onCheckedChange={() => handleToggleEnabled(pair.id)}
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedPair(pair)
                      setIsDetailDialogOpen(true)
                    }}
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Z-Score</div>
                  <div className={`font-bold text-lg ${getZScoreColor(pair.zScore)}`}>
                    {pair.zScore.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground">相関係数</div>
                  <div className="font-medium">{pair.correlation.toFixed(3)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">ベータ</div>
                  <div className="font-medium">{pair.beta.toFixed(3)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">ステータス</div>
                  <Badge variant={pair.enabled ? "default" : "secondary"}>
                    {pair.enabled ? "監視中" : "停止中"}
                  </Badge>
                </div>
              </div>
              
              <div className="pt-2 border-t">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">作成日</span>
                  <span>{pair.createdAt}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detail Dialog */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          {selectedPair && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedPair.name}</DialogTitle>
                <DialogDescription>
                  {selectedPair.symbolA} / {selectedPair.symbolB} - 詳細情報
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6">
                {/* Current Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="pt-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{selectedPair.priceA}</div>
                        <div className="text-sm text-muted-foreground">{selectedPair.symbolA} 価格</div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{selectedPair.priceB}</div>
                        <div className="text-sm text-muted-foreground">{selectedPair.symbolB} 価格</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Z-Score Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Z-Score推移</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={mockZScoreHistory}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke="hsl(var(--primary))" 
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Statistics */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold">{selectedPair.zScore.toFixed(2)}</div>
                    <div className="text-sm text-muted-foreground">Z-Score</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{selectedPair.correlation.toFixed(3)}</div>
                    <div className="text-sm text-muted-foreground">相関係数</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{selectedPair.beta.toFixed(3)}</div>
                    <div className="text-sm text-muted-foreground">ベータ</div>
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {filteredPairs.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">ペアが見つかりません</h3>
              <p className="text-muted-foreground mb-4">
                検索条件に一致するペアがありません
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                新規ペア作成
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
