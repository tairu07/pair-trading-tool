import { useState } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Pair Trading Tool
            </h1>
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ダッシュボード
              </button>
              <button
                onClick={() => setActiveTab('pairs')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'pairs'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ペア管理
              </button>
              <button
                onClick={() => setActiveTab('backtest')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'backtest'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                バックテスト
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'alerts'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                アラート
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && <DashboardContent />}
        {activeTab === 'pairs' && <PairsContent />}
        {activeTab === 'backtest' && <BacktestContent />}
        {activeTab === 'alerts' && <AlertsContent />}
      </main>
    </div>
  )
}

// Dashboard Content
function DashboardContent() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">ダッシュボード</h2>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">P</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      アクティブペア
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      3
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">$</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      総PnL
                    </dt>
                    <dd className="text-lg font-medium text-green-600">
                      +8.4%
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">!</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      アクティブアラート
                    </dt>
                    <dd className="text-lg font-medium text-yellow-600">
                      2
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">T</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      総取引数
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      24
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              最近のアクティビティ
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <p className="text-sm font-medium text-gray-900">トヨタ/ホンダ</p>
                  <p className="text-sm text-gray-500">Z-Score 2.34でショートエントリーシグナル</p>
                </div>
                <span className="text-sm text-gray-500">10:30</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <p className="text-sm font-medium text-gray-900">MUFG/SMFG</p>
                  <p className="text-sm text-gray-500">Z-Score -1.87でロングエントリーシグナル</p>
                </div>
                <span className="text-sm text-gray-500">09:45</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <p className="text-sm font-medium text-gray-900">バックテスト完了</p>
                  <p className="text-sm text-gray-500">トヨタ/ホンダ 基本戦略 - PnL: +8.4%</p>
                </div>
                <span className="text-sm text-gray-500">14:35</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Pairs Content
function PairsContent() {
  const pairs = [
    { id: 1, name: 'トヨタ/ホンダ', symbolA: '7203', symbolB: '7267', zScore: 2.34, status: 'active' },
    { id: 2, name: 'MUFG/SMFG', symbolA: '8306', symbolB: '8316', zScore: -1.87, status: 'active' },
    { id: 3, name: 'ソニー/キーエンス', symbolA: '6758', symbolB: '6861', zScore: 0.45, status: 'inactive' },
  ]

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900">ペア管理</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            新規ペア作成
          </button>
        </div>
        
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {pairs.map((pair) => (
              <li key={pair.id}>
                <div className="px-4 py-4 flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {pair.symbolA.slice(0, 2)}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {pair.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {pair.symbolA} / {pair.symbolB}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">
                        Z-Score: {pair.zScore.toFixed(2)}
                      </div>
                      <div className={`text-sm ${pair.status === 'active' ? 'text-green-600' : 'text-gray-500'}`}>
                        {pair.status === 'active' ? '監視中' : '停止中'}
                      </div>
                    </div>
                    <button className="text-blue-600 hover:text-blue-900">
                      詳細
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

// Backtest Content
function BacktestContent() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900">バックテスト</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            新規バックテスト
          </button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">バックテスト設定</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">ペア選択</label>
                <select className="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                  <option>トヨタ/ホンダ</option>
                  <option>MUFG/SMFG</option>
                  <option>ソニー/キーエンス</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">開始日</label>
                  <input type="date" className="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">終了日</label>
                  <input type="date" className="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">エントリーZ値</label>
                  <input type="number" step="0.1" defaultValue="2.0" className="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">エグジットZ値</label>
                  <input type="number" step="0.1" defaultValue="0.2" className="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
                </div>
              </div>
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
                バックテスト実行
              </button>
            </div>
          </div>
          
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">実行履歴</h3>
            <div className="space-y-3">
              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900">トヨタ/ホンダ 基本戦略</h4>
                    <p className="text-sm text-gray-500">2024-09-25 14:30 - 完了</p>
                  </div>
                  <span className="text-green-600 font-medium">+8.4%</span>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  24取引 | 勝率: 62.5% | シャープレシオ: 1.34
                </div>
              </div>
              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900">MUFG/SMFG 保守戦略</h4>
                    <p className="text-sm text-gray-500">2024-09-26 09:15 - 実行中</p>
                  </div>
                  <span className="text-blue-600 font-medium">67%</span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{width: '67%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Alerts Content
function AlertsContent() {
  const alerts = [
    { id: 1, pair: 'トヨタ/ホンダ', type: 'ENTRY_SHORT', message: 'Z-Score 2.34でショートエントリーシグナル', time: '10:30:15', status: 'active' },
    { id: 2, pair: 'MUFG/SMFG', type: 'ENTRY_LONG', message: 'Z-Score -1.87でロングエントリーシグナル', time: '09:45:22', status: 'delivered' },
    { id: 3, pair: 'ファーストリテイリング/セブン&アイ', type: 'EXIT', message: 'Z-Score -0.15で平均回帰によるエグジット', time: '14:20:10', status: 'completed' },
  ]

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900">アラート管理</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            新規ルール作成
          </button>
        </div>
        
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <li key={alert.id}>
                <div className="px-4 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`flex-shrink-0 h-2 w-2 rounded-full ${
                        alert.status === 'active' ? 'bg-red-400' :
                        alert.status === 'delivered' ? 'bg-blue-400' : 'bg-green-400'
                      }`}></div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {alert.pair}
                        </div>
                        <div className="text-sm text-gray-500">
                          {alert.message}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className={`text-sm font-medium ${
                          alert.type === 'ENTRY_LONG' ? 'text-green-600' :
                          alert.type === 'ENTRY_SHORT' ? 'text-red-600' : 'text-blue-600'
                        }`}>
                          {alert.type}
                        </div>
                        <div className="text-sm text-gray-500">
                          {alert.time}
                        </div>
                      </div>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        alert.status === 'active' ? 'bg-red-100 text-red-800' :
                        alert.status === 'delivered' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {alert.status === 'active' ? 'アクティブ' :
                         alert.status === 'delivered' ? '配信済み' : '完了'}
                      </span>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
