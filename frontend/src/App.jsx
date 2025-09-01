import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  PieChart,
  Settings,
  RefreshCw,
  Send,
  Wifi
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart as RechartsPieChart, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts'
import { LivePortfolio } from './components/LivePortfolio.jsx'
import { WebhookTester } from './components/WebhookTester.jsx'
import { usePortfolioData, useOrderHistory } from './hooks/useApi.js'
import './App.css'

// Mock data for charts and backtesting
const mockPortfolioData = [
  { date: '2025-08-01', value: 10000, pnl: 0 },
  { date: '2025-08-05', value: 10150, pnl: 150 },
  { date: '2025-08-10', value: 9980, pnl: -20 },
  { date: '2025-08-15', value: 10300, pnl: 300 },
  { date: '2025-08-20', value: 10180, pnl: 180 },
  { date: '2025-08-25', value: 10450, pnl: 450 },
  { date: '2025-09-01', value: 10234, pnl: 234 }
]

const mockSignals = [
  { symbol: 'BTC-USD', type: 'BUY', strength: 'STRONG', confidence: 0.85, reasoning: 'Golden cross detected', time: '07:25:00' },
  { symbol: 'ETH-USD', type: 'SELL', strength: 'MODERATE', confidence: 0.72, reasoning: 'RSI overbought', time: '07:20:00' },
  { symbol: 'AAPL', type: 'BUY', strength: 'WEAK', confidence: 0.65, reasoning: 'Support bounce', time: '07:15:00' }
]

const mockBacktestData = [
  { strategy: 'Technical Analysis', return: -2.34, sharpe: -1.93, maxDD: 4.17, trades: 240, winRate: 48.8 },
  { strategy: 'Sentiment Based', return: 5.67, sharpe: 1.24, maxDD: 8.32, trades: 156, winRate: 52.6 },
  { strategy: 'Combined Strategy', return: 3.21, sharpe: 0.89, maxDD: 6.15, trades: 198, winRate: 50.5 }
]

function App() {
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [activeTab, setActiveTab] = useState('overview')
  
  // API hooks
  const { portfolioData, isLoading: portfolioLoading } = usePortfolioData()
  const { orders, isLoading: ordersLoading } = useOrderHistory()

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date())
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status) => {
    switch (status) {
      case 'FILLED': return 'bg-green-500'
      case 'REJECTED': return 'bg-red-500'
      case 'PENDING': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getSignalColor = (type) => {
    return type === 'BUY' ? 'text-green-600' : 'text-red-600'
  }

  const getStrengthColor = (strength) => {
    switch (strength) {
      case 'STRONG': return 'bg-green-100 text-green-800'
      case 'MODERATE': return 'bg-yellow-100 text-yellow-800'
      case 'WEAK': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Calculate metrics from real data
  const totalWebhooks = portfolioData?.webhook_stats?.total_webhooks || 0
  const successfulOrders = portfolioData?.webhook_stats?.successful_orders || 0
  const failedOrders = portfolioData?.webhook_stats?.failed_orders || 0
  const isConnected = portfolioData?.broker_status?.PAPER_TRADING?.connected || false

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Trading System Dashboard</h1>
            <p className="text-gray-600">Real-time monitoring and control</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <Button variant="outline" size="sm" onClick={() => setLastUpdate(new Date())}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Status Alert */}
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            System operational. Last update: {lastUpdate.toLocaleTimeString()}
            {portfolioData?.webhook_stats?.last_webhook && (
              <span className="ml-4">
                Last webhook: {new Date(portfolioData.webhook_stats.last_webhook).toLocaleTimeString()}
              </span>
            )}
          </AlertDescription>
        </Alert>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Webhooks</CardTitle>
              <Send className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalWebhooks}</div>
              <p className="text-xs text-muted-foreground">
                Processed signals
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Successful Orders</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{successfulOrders}</div>
              <p className="text-xs text-muted-foreground">
                Executed successfully
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Failed Orders</CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{failedOrders}</div>
              <p className="text-xs text-muted-foreground">
                Rejected or failed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {totalWebhooks > 0 ? ((successfulOrders / totalWebhooks) * 100).toFixed(0) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Order execution rate
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="signals">Signals</TabsTrigger>
            <TabsTrigger value="webhook">Webhook</TabsTrigger>
            <TabsTrigger value="backtest">Backtest</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Portfolio Performance Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Portfolio Performance</CardTitle>
                  <CardDescription>30-day portfolio value trend</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={mockPortfolioData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Webhook Activity Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Webhook Activity</CardTitle>
                  <CardDescription>Success vs failure rate</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={[
                      { name: 'Successful', value: successfulOrders, fill: '#10b981' },
                      { name: 'Failed', value: failedOrders, fill: '#ef4444' }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest system events and alerts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {portfolioData?.recent_orders?.slice(0, 5).map((order, index) => (
                    <div key={index} className="flex items-center space-x-4">
                      {order.status === 'FILLED' ? 
                        <CheckCircle className="w-5 h-5 text-green-500" /> :
                        <XCircle className="w-5 h-5 text-red-500" />
                      }
                      <div className="flex-1">
                        <p className="text-sm font-medium">
                          Order {order.symbol} {order.side} {order.status.toLowerCase()}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(order.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  )) || (
                    <div className="text-center py-4 text-gray-500">
                      No recent activity
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Portfolio Tab */}
          <TabsContent value="portfolio" className="space-y-6">
            <LivePortfolio />
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Order History</CardTitle>
                <CardDescription>Recent trading orders and their status</CardDescription>
              </CardHeader>
              <CardContent>
                {ordersLoading ? (
                  <div className="flex items-center justify-center h-32">
                    <RefreshCw className="w-6 h-6 animate-spin mr-2" />
                    <span>Loading orders...</span>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {orders.length > 0 ? orders.map((order, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(order.status)}`}></div>
                          <div>
                            <p className="font-medium">{order.symbol}</p>
                            <p className="text-sm text-gray-500">{order.id}</p>
                          </div>
                        </div>
                        <div className="text-center">
                          <p className={`font-medium ${order.side === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                            {order.side}
                          </p>
                          <p className="text-sm text-gray-500">{order.quantity}</p>
                        </div>
                        <div className="text-center">
                          <p className="font-medium">${order.price?.toLocaleString()}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(order.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge variant={order.status === 'FILLED' ? 'default' : 'destructive'}>
                            {order.status}
                          </Badge>
                          <p className="text-sm text-gray-500">{order.broker}</p>
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-8 text-gray-500">
                        No orders found
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Signals Tab */}
          <TabsContent value="signals" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Trading Signals</CardTitle>
                <CardDescription>AI-generated trading signals and recommendations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockSignals.map((signal, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`p-2 rounded-full ${signal.type === 'BUY' ? 'bg-green-100' : 'bg-red-100'}`}>
                          {signal.type === 'BUY' ? 
                            <TrendingUp className="w-4 h-4 text-green-600" /> : 
                            <TrendingDown className="w-4 h-4 text-red-600" />
                          }
                        </div>
                        <div>
                          <p className="font-medium">{signal.symbol}</p>
                          <p className="text-sm text-gray-500">{signal.reasoning}</p>
                        </div>
                      </div>
                      <div className="text-center">
                        <p className={`font-medium ${getSignalColor(signal.type)}`}>
                          {signal.type}
                        </p>
                        <Badge className={getStrengthColor(signal.strength)}>
                          {signal.strength}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{(signal.confidence * 100).toFixed(0)}%</p>
                        <p className="text-sm text-gray-500">{signal.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Webhook Tab */}
          <TabsContent value="webhook" className="space-y-6">
            <WebhookTester />
          </TabsContent>

          {/* Backtest Tab */}
          <TabsContent value="backtest" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Strategy Backtesting</CardTitle>
                <CardDescription>Historical performance of different trading strategies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockBacktestData.map((strategy, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="font-medium">{strategy.strategy}</h3>
                        <Badge variant={strategy.return >= 0 ? 'default' : 'destructive'}>
                          {strategy.return >= 0 ? '+' : ''}{strategy.return.toFixed(2)}%
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Sharpe Ratio</p>
                          <p className="font-medium">{strategy.sharpe.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Max Drawdown</p>
                          <p className="font-medium">{strategy.maxDD.toFixed(2)}%</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Total Trades</p>
                          <p className="font-medium">{strategy.trades}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Win Rate</p>
                          <p className="font-medium">{strategy.winRate.toFixed(1)}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

