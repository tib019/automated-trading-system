import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Wifi, 
  WifiOff,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { usePortfolioData, useBrokerStatus } from '../hooks/useApi.js'

export const LivePortfolio = () => {
  const { portfolioData, isLoading: portfolioLoading, error: portfolioError, refetch: refetchPortfolio } = usePortfolioData()
  const { brokerStatus, isLoading: brokerLoading, error: brokerError, refetch: refetchBroker } = useBrokerStatus()
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date())
    }, 1000)
    
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    refetchPortfolio()
    refetchBroker()
    setLastUpdate(new Date())
  }

  const calculateTotalBalance = () => {
    if (!brokerStatus.PAPER_TRADING?.balances) return 0
    
    const balances = brokerStatus.PAPER_TRADING.balances
    let total = 0
    
    // Add USD balance
    if (balances.USD) {
      total += balances.USD.total || 0
    }
    
    // Add crypto/stock values (simplified calculation)
    if (balances.BTC) {
      total += (balances.BTC.total || 0) * 52000 // Assume BTC price
    }
    if (balances.AAPL) {
      total += (balances.AAPL.total || 0) * 185 // Assume AAPL price
    }
    
    return total
  }

  const getConnectionStatus = () => {
    if (brokerStatus.PAPER_TRADING?.connected) {
      return { status: 'connected', color: 'text-green-600', icon: Wifi }
    }
    return { status: 'disconnected', color: 'text-red-600', icon: WifiOff }
  }

  const connectionStatus = getConnectionStatus()
  const totalBalance = calculateTotalBalance()
  const initialBalance = 100000
  const totalPnL = totalBalance - initialBalance
  const totalPnLPercent = (totalPnL / initialBalance) * 100

  if (portfolioLoading || brokerLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="flex items-center justify-center h-32">
            <RefreshCw className="w-6 h-6 animate-spin mr-2" />
            <span>Loading portfolio data...</span>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Alert>
        <connectionStatus.icon className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>
            Broker Status: <span className={connectionStatus.color}>{connectionStatus.status}</span>
            {' • '}Last Update: {lastUpdate.toLocaleTimeString()}
          </span>
          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </AlertDescription>
      </Alert>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Portfolio Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              Initial: ${initialBalance.toLocaleString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total P&L</CardTitle>
            {totalPnL >= 0 ? 
              <TrendingUp className="h-4 w-4 text-green-600" /> : 
              <TrendingDown className="h-4 w-4 text-red-600" />
            }
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}
            </div>
            <p className={`text-xs ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalPnL >= 0 ? '+' : ''}{totalPnLPercent.toFixed(2)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Positions</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {brokerStatus.PAPER_TRADING?.position_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Paper Trading
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Asset Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Asset Breakdown</CardTitle>
          <CardDescription>Current holdings across all assets</CardDescription>
        </CardHeader>
        <CardContent>
          {brokerStatus.PAPER_TRADING?.balances ? (
            <div className="space-y-4">
              {Object.entries(brokerStatus.PAPER_TRADING.balances).map(([asset, balance]) => {
                const total = balance.total || 0
                if (total <= 0.001) return null // Skip very small balances
                
                let displayValue = total
                let valueUSD = total
                
                // Calculate USD value for non-USD assets
                if (asset === 'BTC') {
                  valueUSD = total * 52000 // Simplified price
                  displayValue = `${total.toFixed(6)} BTC`
                } else if (asset === 'AAPL') {
                  valueUSD = total * 185 // Simplified price
                  displayValue = `${total.toFixed(2)} shares`
                } else if (asset === 'USD') {
                  displayValue = `$${total.toFixed(2)}`
                }
                
                const percentage = (valueUSD / totalBalance) * 100
                
                return (
                  <div key={asset} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">{asset}</span>
                      </div>
                      <div>
                        <p className="font-medium">{asset}</p>
                        <p className="text-sm text-gray-500">{displayValue}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">${valueUSD.toFixed(2)}</p>
                      <p className="text-sm text-gray-500">{percentage.toFixed(1)}%</p>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No balance data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Webhook Statistics */}
      {portfolioData?.webhook_stats && (
        <Card>
          <CardHeader>
            <CardTitle>Trading Activity</CardTitle>
            <CardDescription>Recent webhook and order statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {portfolioData.webhook_stats.total_webhooks}
                </div>
                <p className="text-sm text-gray-500">Total Webhooks</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {portfolioData.webhook_stats.successful_orders}
                </div>
                <p className="text-sm text-gray-500">Successful Orders</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {portfolioData.webhook_stats.failed_orders}
                </div>
                <p className="text-sm text-gray-500">Failed Orders</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {portfolioData.webhook_stats.successful_orders > 0 ? 
                    ((portfolioData.webhook_stats.successful_orders / portfolioData.webhook_stats.total_webhooks) * 100).toFixed(0) : 0}%
                </div>
                <p className="text-sm text-gray-500">Success Rate</p>
              </div>
            </div>
            
            {portfolioData.webhook_stats.last_webhook && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-500">
                  Last webhook: {new Date(portfolioData.webhook_stats.last_webhook).toLocaleString()}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {(portfolioError || brokerError) && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {portfolioError || brokerError}
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}

