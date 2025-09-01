import { useState, useEffect, useCallback } from 'react'

const API_BASE_URL = 'http://localhost:5000'

export const useApi = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const apiCall = useCallback(async (endpoint, options = {}) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { apiCall, isLoading, error }
}

export const usePortfolioData = () => {
  const [portfolioData, setPortfolioData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const { apiCall } = useApi()

  const fetchPortfolioData = useCallback(async () => {
    try {
      const data = await apiCall('/status')
      setPortfolioData(data)
    } catch (err) {
      setError(err.message)
      // Fallback to mock data if API is not available
      setPortfolioData({
        webhook_stats: {
          total_webhooks: 5,
          successful_orders: 2,
          failed_orders: 3,
          last_webhook: new Date().toISOString()
        },
        broker_status: {
          PAPER_TRADING: {
            connected: true,
            balances: {
              USD: { total: 94113.54 },
              BTC: { total: 0.08 },
              AAPL: { total: 10.67 }
            },
            positions: []
          }
        },
        recent_orders: []
      })
    } finally {
      setIsLoading(false)
    }
  }, [apiCall])

  useEffect(() => {
    fetchPortfolioData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchPortfolioData, 30000)
    return () => clearInterval(interval)
  }, [fetchPortfolioData])

  return { portfolioData, isLoading, error, refetch: fetchPortfolioData }
}

export const useOrderHistory = () => {
  const [orders, setOrders] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const { apiCall } = useApi()

  const fetchOrders = useCallback(async (limit = 50) => {
    try {
      const data = await apiCall(`/orders?limit=${limit}`)
      setOrders(data.orders || [])
    } catch (err) {
      setError(err.message)
      // Fallback to mock data
      setOrders([
        {
          id: 'ORDER_001',
          symbol: 'BTC-USD',
          side: 'BUY',
          quantity: 0.04,
          price: 50000,
          status: 'FILLED',
          created_at: new Date().toISOString(),
          broker: 'PAPER_TRADING'
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }, [apiCall])

  useEffect(() => {
    fetchOrders()
  }, [fetchOrders])

  return { orders, isLoading, error, refetch: fetchOrders }
}

export const useBrokerStatus = () => {
  const [brokerStatus, setBrokerStatus] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const { apiCall } = useApi()

  const fetchBrokerStatus = useCallback(async () => {
    try {
      const data = await apiCall('/brokers')
      setBrokerStatus(data)
    } catch (err) {
      setError(err.message)
      // Fallback to mock data
      setBrokerStatus({
        PAPER_TRADING: {
          connected: true,
          balances: {
            USD: { total: 94113.54, free: 94113.54, locked: 0 },
            BTC: { total: 0.08, free: 0.08, locked: 0 },
            AAPL: { total: 10.67, free: 10.67, locked: 0 }
          },
          positions: [],
          position_count: 0
        }
      })
    } finally {
      setIsLoading(false)
    }
  }, [apiCall])

  useEffect(() => {
    fetchBrokerStatus()
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchBrokerStatus, 10000)
    return () => clearInterval(interval)
  }, [fetchBrokerStatus])

  return { brokerStatus, isLoading, error, refetch: fetchBrokerStatus }
}

export const useWebhookTest = () => {
  const { apiCall } = useApi()

  const sendTestWebhook = useCallback(async (signalData) => {
    try {
      const response = await apiCall('/webhook/test', {
        method: 'POST',
        body: JSON.stringify(signalData)
      })
      return response
    } catch (err) {
      throw err
    }
  }, [apiCall])

  const sendCustomWebhook = useCallback(async (signalData) => {
    try {
      const response = await apiCall('/webhook/tradingview', {
        method: 'POST',
        body: JSON.stringify(signalData)
      })
      return response
    } catch (err) {
      throw err
    }
  }, [apiCall])

  return { sendTestWebhook, sendCustomWebhook }
}

