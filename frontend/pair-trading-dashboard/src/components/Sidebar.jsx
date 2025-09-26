import { Link, useLocation } from 'react-router-dom'
import { 
  BarChart3, 
  TrendingUp, 
  Bell, 
  Database, 
  Settings, 
  Moon, 
  Sun,
  ChevronLeft,
  ChevronRight,
  Activity
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'ダッシュボード', href: '/', icon: BarChart3 },
  { name: 'ペア管理', href: '/pairs', icon: TrendingUp },
  { name: 'バックテスト', href: '/backtest', icon: Activity },
  { name: 'アラート', href: '/alerts', icon: Bell },
  { name: 'マーケットデータ', href: '/market-data', icon: Database },
]

export function Sidebar({ open, setOpen, darkMode, toggleDarkMode }) {
  const location = useLocation()

  return (
    <div className={cn(
      "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300",
      open ? "w-64" : "w-16"
    )}>
      <div className="flex h-full flex-col">
        {/* Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-sidebar-border">
          {open && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-semibold text-sidebar-foreground">Pair Trading</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setOpen(!open)}
            className="text-sidebar-foreground hover:bg-sidebar-accent"
          >
            {open ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  !open && "justify-center"
                )}
              >
                <item.icon className={cn("w-5 h-5", open && "mr-3")} />
                {open && <span>{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="flex items-center justify-between">
            {open && (
              <span className="text-sm text-sidebar-foreground">テーマ</span>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleDarkMode}
              className="text-sidebar-foreground hover:bg-sidebar-accent"
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
