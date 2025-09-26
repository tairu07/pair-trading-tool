import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Bell, 
  Plus, 
  Search, 
  Filter, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Settings,
  Trash2,
  Edit
} from 'lucide-react'

// Mock data
const mockAlerts = [
  {
    id: 1,
    pair: 'トヨタ/ホンダ',
    symbolA: '7203',
    symbolB: '7267',
    type: 'ENTRY_SHORT',
    message: 'Z-Score 2.34でショートエントリーシグナル',
    zScore: 2.34,
    status: 'active',
    createdAt: '2024-09-26 10:30:15',
    deliveredAt: null
  },
  {
    id: 2,
    pair: 'MUFG/SMFG',
    symbolA: '8306',
    symbolB: '8316',
    type: 'ENTRY_LONG',
    message: 'Z-Score -1.87でロングエントリーシグナル',
    zScore: -1.87,
    status: 'delivered',
    createdAt: '2024-09-26 09:45:22',
    deliveredAt: '2024-09-26 09:45:25'
  },
  {
    id: 3,
    pair: 'ファーストリテイリング/セブン&アイ',
    symbolA: '9983',
    symbolB: '3382',
    type: 'EXIT',
    message: 'Z-Score -0.15で平均回帰によるエグジット',
    zScore: -0.15,
    status: 'completed',
    createdAt: '2024-09-25 14:20:10',
    deliveredAt: '2024-09-25 14:20:12'
  }
]

const mockAlertRules = [
  {
    id: 1,
    pairId: 1,
    pair: 'トヨタ/ホンダ',
    name: 'エントリーシグナル',
    description: 'Z-Score ±2.0でエントリーアラート',
    enabled: true,
    params: {
      entryThreshold: 2.0,
      exitThreshold: 0.2,
      channels: ['discord', 'email']
    },
    createdAt: '2024-09-20'
  },
  {
    id: 2,
    pairId: 2,
    pair: 'MUFG/SMFG',
    name: '保守的エントリー',
    description: 'Z-Score ±2.5でエントリーアラート',
    enabled: true,
    params: {
      entryThreshold: 2.5,
      exitThreshold: 0.1,
      channels: ['discord']
    },
    createdAt: '2024-09-18'
  },
  {
    id: 3,
    pairId: 3,
    pair: 'ソニー/キーエンス',
    name: 'テスト用ルール',
    description: 'テスト用のアラートルール',
    enabled: false,
    params: {
      entryThreshold: 1.5,
      exitThreshold: 0.3,
      channels: ['email']
    },
    createdAt: '2024-09-15'
  }
]

export function AlertsPage() {
  const [activeTab, setActiveTab] = useState('alerts')
  const [alerts, setAlerts] = useState(mockAlerts)
  const [rules, setRules] = useState(mockAlertRules)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [isCreateRuleDialogOpen, setIsCreateRuleDialogOpen] = useState(false)

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.pair.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.type.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || alert.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const filteredRules = rules.filter(rule => {
    const matchesSearch = rule.pair.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rule.name.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSearch
  })

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <AlertTriangle className="w-4 h-4 text-orange-500" />
      case 'delivered': return <Clock className="w-4 h-4 text-blue-500" />
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      default: return <Bell className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return 'destructive'
      case 'delivered': return 'secondary'
      case 'completed': return 'default'
      default: return 'outline'
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'ENTRY_LONG': return 'text-green-600'
      case 'ENTRY_SHORT': return 'text-red-600'
      case 'EXIT': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }

  const handleToggleRule = (id) => {
    setRules(rules.map(rule => 
      rule.id === id ? { ...rule, enabled: !rule.enabled } : rule
    ))
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">アラート管理</h1>
          <p className="text-muted-foreground">
            トレーディングシグナルとアラートルールの管理
          </p>
        </div>
        <Dialog open={isCreateRuleDialogOpen} onOpenChange={setIsCreateRuleDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="w-4 h-4" />
              新規ルール作成
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>新規アラートルール作成</DialogTitle>
              <DialogDescription>
                新しいアラートルールを作成します
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="ruleName">ルール名</Label>
                <Input id="ruleName" placeholder="エントリーシグナル" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="pair">対象ペア</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="ペアを選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">トヨタ/ホンダ</SelectItem>
                    <SelectItem value="2">MUFG/SMFG</SelectItem>
                    <SelectItem value="3">ソニー/キーエンス</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="entryThreshold">エントリー閾値</Label>
                  <Input id="entryThreshold" type="number" step="0.1" placeholder="2.0" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="exitThreshold">エグジット閾値</Label>
                  <Input id="exitThreshold" type="number" step="0.1" placeholder="0.2" />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="enabled" />
                <Label htmlFor="enabled">ルールを有効にする</Label>
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setIsCreateRuleDialogOpen(false)}>
                キャンセル
              </Button>
              <Button onClick={() => setIsCreateRuleDialogOpen(false)}>
                作成
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="alerts">アラート履歴</TabsTrigger>
          <TabsTrigger value="rules">アラートルール</TabsTrigger>
        </TabsList>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                    <Input
                      placeholder="ペア名、アラートタイプで検索..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <Filter className="w-4 h-4 mr-2" />
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">すべて</SelectItem>
                    <SelectItem value="active">アクティブ</SelectItem>
                    <SelectItem value="delivered">配信済み</SelectItem>
                    <SelectItem value="completed">完了</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Alerts List */}
          <div className="space-y-4">
            {filteredAlerts.map((alert) => (
              <Card key={alert.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getStatusIcon(alert.status)}
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium">{alert.pair}</h3>
                          <Badge variant={getStatusBadge(alert.status)}>
                            {alert.status === 'active' && 'アクティブ'}
                            {alert.status === 'delivered' && '配信済み'}
                            {alert.status === 'completed' && '完了'}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{alert.message}</p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <span>作成: {alert.createdAt}</span>
                          {alert.deliveredAt && <span>配信: {alert.deliveredAt}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-lg font-bold ${getTypeColor(alert.type)}`}>
                        {alert.type}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Z: {alert.zScore.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredAlerts.length === 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <Bell className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">アラートが見つかりません</h3>
                  <p className="text-muted-foreground">
                    検索条件に一致するアラートがありません
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Rules Tab */}
        <TabsContent value="rules" className="space-y-6">
          {/* Rules List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRules.map((rule) => (
              <Card key={rule.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{rule.name}</CardTitle>
                      <CardDescription>{rule.pair}</CardDescription>
                    </div>
                    <Switch
                      checked={rule.enabled}
                      onCheckedChange={() => handleToggleRule(rule.id)}
                    />
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{rule.description}</p>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">エントリー閾値:</span>
                      <span className="font-medium">±{rule.params.entryThreshold}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">エグジット閾値:</span>
                      <span className="font-medium">±{rule.params.exitThreshold}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">通知チャンネル:</span>
                      <span className="font-medium">{rule.params.channels.length}個</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-2 border-t">
                    <span className="text-xs text-muted-foreground">
                      作成: {rule.createdAt}
                    </span>
                    <div className="flex space-x-1">
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredRules.length === 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <Settings className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">アラートルールが見つかりません</h3>
                  <p className="text-muted-foreground mb-4">
                    検索条件に一致するルールがありません
                  </p>
                  <Button onClick={() => setIsCreateRuleDialogOpen(true)}>
                    新規ルール作成
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
