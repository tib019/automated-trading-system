import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Send, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { useWebhookTest } from '../hooks/useApi.js'

export const WebhookTester = () => {
  const [formData, setFormData] = useState({
    ticker: 'BTC-USD',
    action: 'BUY',
    price: '50000',
    strength: 'MODERATE',
    stop_loss: '',
    take_profit: '',
    position_size: '2.0',
    message: 'Test signal from dashboard',
    confidence_score: '0.75'
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  
  const { sendTestWebhook, sendCustomWebhook } = useWebhookTest()

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Auto-calculate stop loss and take profit
    if (field === 'price' || field === 'action') {
      const price = parseFloat(field === 'price' ? value : formData.price)
      const action = field === 'action' ? value : formData.action
      
      if (price && action) {
        if (action === 'BUY') {
          setFormData(prev => ({
            ...prev,
            stop_loss: (price * 0.95).toFixed(2),
            take_profit: (price * 1.10).toFixed(2)
          }))
        } else {
          setFormData(prev => ({
            ...prev,
            stop_loss: (price * 1.05).toFixed(2),
            take_profit: (price * 0.90).toFixed(2)
          }))
        }
      }
    }
  }

  const handleTestWebhook = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const response = await sendTestWebhook()
      setResult(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCustomWebhook = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const signalData = {
        ...formData,
        price: parseFloat(formData.price),
        stop_loss: parseFloat(formData.stop_loss),
        take_profit: parseFloat(formData.take_profit),
        position_size: parseFloat(formData.position_size),
        confidence_score: parseFloat(formData.confidence_score)
      }
      
      const response = await sendCustomWebhook(signalData)
      setResult(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const presetSignals = [
    {
      name: 'Bitcoin Bullish',
      data: {
        ticker: 'BTC-USD',
        action: 'BUY',
        price: '52000',
        strength: 'STRONG',
        message: 'Golden cross detected on 4H chart',
        confidence_score: '0.85'
      }
    },
    {
      name: 'Ethereum Bearish',
      data: {
        ticker: 'ETH-USD',
        action: 'SELL',
        price: '3500',
        strength: 'MODERATE',
        message: 'RSI overbought + resistance level',
        confidence_score: '0.72'
      }
    },
    {
      name: 'Apple Breakout',
      data: {
        ticker: 'AAPL',
        action: 'BUY',
        price: '185',
        strength: 'WEAK',
        message: 'Support bounce + volume increase',
        confidence_score: '0.65'
      }
    }
  ]

  const loadPreset = (preset) => {
    setFormData(prev => ({ ...prev, ...preset.data }))
    handleInputChange('price', preset.data.price)
  }

  return (
    <div className="space-y-6">
      {/* Preset Signals */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Test Signals</CardTitle>
          <CardDescription>Pre-configured signals for quick testing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button 
              variant="outline" 
              onClick={handleTestWebhook}
              disabled={isLoading}
            >
              {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
              Default Test Signal
            </Button>
            {presetSignals.map((preset, index) => (
              <Button 
                key={index}
                variant="outline" 
                onClick={() => loadPreset(preset)}
              >
                {preset.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Custom Signal Form */}
      <Card>
        <CardHeader>
          <CardTitle>Custom Signal Generator</CardTitle>
          <CardDescription>Create and send custom trading signals</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="ticker">Symbol</Label>
              <Input
                id="ticker"
                value={formData.ticker}
                onChange={(e) => handleInputChange('ticker', e.target.value)}
                placeholder="BTC-USD"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="action">Action</Label>
              <Select value={formData.action} onValueChange={(value) => handleInputChange('action', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BUY">BUY</SelectItem>
                  <SelectItem value="SELL">SELL</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="price">Price</Label>
              <Input
                id="price"
                type="number"
                value={formData.price}
                onChange={(e) => handleInputChange('price', e.target.value)}
                placeholder="50000"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="strength">Strength</Label>
              <Select value={formData.strength} onValueChange={(value) => handleInputChange('strength', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="WEAK">WEAK</SelectItem>
                  <SelectItem value="MODERATE">MODERATE</SelectItem>
                  <SelectItem value="STRONG">STRONG</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="stop_loss">Stop Loss</Label>
              <Input
                id="stop_loss"
                type="number"
                value={formData.stop_loss}
                onChange={(e) => handleInputChange('stop_loss', e.target.value)}
                placeholder="Auto-calculated"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="take_profit">Take Profit</Label>
              <Input
                id="take_profit"
                type="number"
                value={formData.take_profit}
                onChange={(e) => handleInputChange('take_profit', e.target.value)}
                placeholder="Auto-calculated"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="position_size">Position Size (%)</Label>
              <Input
                id="position_size"
                type="number"
                step="0.1"
                value={formData.position_size}
                onChange={(e) => handleInputChange('position_size', e.target.value)}
                placeholder="2.0"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="confidence_score">Confidence Score</Label>
              <Input
                id="confidence_score"
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={formData.confidence_score}
                onChange={(e) => handleInputChange('confidence_score', e.target.value)}
                placeholder="0.75"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="message">Message</Label>
            <Textarea
              id="message"
              value={formData.message}
              onChange={(e) => handleInputChange('message', e.target.value)}
              placeholder="Signal reasoning or description"
              rows={3}
            />
          </div>
          
          <Button 
            onClick={handleCustomWebhook} 
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
            Send Custom Signal
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {result.success ? 
                <CheckCircle className="w-5 h-5 text-green-500" /> : 
                <XCircle className="w-5 h-5 text-red-500" />
              }
              <span>Webhook Result</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Badge variant={result.success ? 'default' : 'destructive'}>
                  {result.success ? 'SUCCESS' : 'FAILED'}
                </Badge>
                <span className="text-sm text-gray-500">
                  {new Date(result.timestamp).toLocaleTimeString()}
                </span>
              </div>
              
              {result.success && result.signal && (
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Signal Processed</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-green-600">Symbol:</span> {result.signal.symbol}
                    </div>
                    <div>
                      <span className="text-green-600">Action:</span> {result.signal.action}
                    </div>
                    <div>
                      <span className="text-green-600">Price:</span> ${result.signal.price}
                    </div>
                    <div>
                      <span className="text-green-600">Strength:</span> {result.signal.strength}
                    </div>
                  </div>
                  {result.broker && (
                    <div className="mt-2 text-sm">
                      <span className="text-green-600">Broker:</span> {result.broker}
                    </div>
                  )}
                </div>
              )}
              
              {result.message && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Message</h4>
                  <p className="text-sm text-blue-700">{result.message}</p>
                </div>
              )}
              
              {result.error && (
                <div className="p-4 bg-red-50 rounded-lg">
                  <h4 className="font-medium text-red-800 mb-2">Error</h4>
                  <p className="text-sm text-red-700">{result.error}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to send webhook: {error}
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}

