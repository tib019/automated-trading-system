# Trading System API - Referenz

**Version:** 1.0.0  
**Base URL:** `http://localhost:5001/api`  
**Content-Type:** `application/json`  

## Authentifizierung

```bash
# API-Key Header
X-API-Key: your_api_key

# Bearer Token
Authorization: Bearer your_token
```

## System Endpoints

### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Trading System API",
  "version": "1.0.0",
  "components": {
    "data_collector": "active",
    "signal_generator": "active",
    "risk_manager": "active"
  }
}
```

### System Status
```http
GET /status
```
**Response:**
```json
{
  "status": "operational",
  "timestamp": "2025-09-01T08:00:00Z",
  "portfolio": {
    "total_value": 100000,
    "cash_balance": 95000,
    "risk_level": "LOW"
  },
  "trading": {
    "recent_orders": 6
  },
  "security": {
    "events_24h": 12
  }
}
```

## Portfolio Endpoints

### Portfolio Status
```http
GET /portfolio/status
```
**Response:**
```json
{
  "status": "success",
  "portfolio": {
    "total_value": 100000,
    "cash_balance": 95000,
    "unrealized_pnl": 500,
    "realized_pnl": -200,
    "positions": [
      {
        "symbol": "BTC-USD",
        "quantity": 0.08,
        "avg_price": 50000,
        "current_price": 50500,
        "market_value": 4040,
        "unrealized_pnl": 40,
        "pnl_percent": 1.0
      }
    ],
    "risk_metrics": {
      "portfolio_risk": "LOW",
      "max_drawdown": 2.5,
      "sharpe_ratio": 1.8
    }
  }
}
```

### Get Positions
```http
GET /portfolio/positions?symbol=BTC-USD&status=open
```

### Portfolio Performance
```http
GET /portfolio/performance?days=30
```

## Order Management

### Get Orders
```http
GET /orders?limit=50&status=FILLED&symbol=BTC-USD
```
**Response:**
```json
{
  "status": "success",
  "orders": [
    {
      "id": "order_123",
      "symbol": "BTC-USD",
      "side": "BUY",
      "quantity": 0.08,
      "price": 50000,
      "status": "FILLED",
      "timestamp": "2025-09-01T07:30:00Z"
    }
  ],
  "count": 1
}
```

### Create Order
```http
POST /orders
Content-Type: application/json
Authorization: Bearer token

{
  "symbol": "BTC-USD",
  "side": "BUY",
  "quantity": 0.1,
  "order_type": "MARKET",
  "stop_loss": 48000,
  "take_profit": 55000
}
```
**Response:**
```json
{
  "status": "success",
  "order": {
    "id": "order_124",
    "symbol": "BTC-USD",
    "side": "BUY",
    "quantity": 0.1,
    "status": "PENDING"
  }
}
```

### Cancel Order
```http
POST /orders/{order_id}/cancel
Authorization: Bearer token
```

### Validate Order
```http
POST /orders/validate
Content-Type: application/json

{
  "symbol": "BTC-USD",
  "side": "BUY",
  "quantity": 0.1,
  "price": 50000
}
```

## Signal Generation

### Get Recommendations
```http
GET /signals/recommendations
```
**Response:**
```json
{
  "status": "success",
  "recommendations": [
    {
      "symbol": "BTC-USD",
      "action": "BUY",
      "strength": "MODERATE",
      "confidence": 0.75,
      "price": 50500,
      "reasoning": "Bullish sentiment + oversold RSI",
      "entry_price": 50400,
      "stop_loss": 48900,
      "take_profit": 55200
    }
  ]
}
```

### Generate Signal
```http
POST /signals/generate
Content-Type: application/json

{
  "market_data": {
    "symbol": "BTC-USD",
    "price": 50500,
    "volume": 1000000
  },
  "sentiment_data": {
    "sentiment_score": 0.3,
    "confidence": 0.7
  }
}
```

### Technical Indicators
```http
GET /signals/technical-indicators/BTC-USD
```
**Response:**
```json
{
  "status": "success",
  "symbol": "BTC-USD",
  "indicators": {
    "sma_20": 49800,
    "ema_12": 50100,
    "rsi": 45.2,
    "macd": {
      "macd": 120.5,
      "signal": 115.2,
      "histogram": 5.3
    },
    "bollinger_bands": {
      "upper": 52000,
      "middle": 50000,
      "lower": 48000
    }
  }
}
```

## Trading Operations

### Collect Data
```http
POST /trading/collect-data
Content-Type: application/json

{
  "symbols": ["BTC-USD", "ETH-USD", "AAPL"]
}
```

### Auto Trade
```http
POST /trading/auto-trade
Content-Type: application/json

{
  "symbol": "BTC-USD"
}
```

### Get Symbols
```http
GET /trading/symbols
```
**Response:**
```json
{
  "status": "success",
  "symbols": {
    "crypto": ["BTC-USD", "ETH-USD"],
    "stocks": ["AAPL", "TSLA"],
    "all": ["BTC-USD", "ETH-USD", "AAPL", "TSLA"]
  }
}
```

## Security Endpoints

### Security Events
```http
GET /security/events?hours=24
```

### Security Audit
```http
POST /security/audit
Authorization: Bearer token
```

### Validate Signature
```http
POST /security/validate-signature
Content-Type: application/json

{
  "payload": "webhook_data",
  "signature": "sha256=hash",
  "secret": "webhook_secret"
}
```

## Emergency Endpoints

### Kill Switch
```http
POST /emergency/kill-switch
Authorization: Bearer token
```
**Response:**
```json
{
  "status": "success",
  "message": "Kill switch activated",
  "result": {
    "positions_closed": 3,
    "orders_cancelled": 2,
    "portfolio_protected": true
  }
}
```

## Webhook Integration

### TradingView Webhook
```http
POST /webhook/tradingview
Content-Type: application/json
X-Signature: sha256=signature

{
  "symbol": "BTCUSD",
  "action": "BUY",
  "price": 50500,
  "time": "2025-09-01T08:00:00Z"
}
```

## Error Responses

### Standard Error Format
```json
{
  "status": "error",
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-01T08:00:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| General API | 100 requests | 1 minute |
| Webhooks | 60 requests | 1 minute |
| Authentication | 5 requests | 5 minutes |
| Emergency | 10 requests | 1 hour |

## Response Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1693555200
Content-Type: application/json
```

## Examples

### Complete Trading Workflow
```bash
# 1. Check system health
curl http://localhost:5001/api/health

# 2. Get portfolio status
curl http://localhost:5001/api/portfolio/status

# 3. Get trading recommendations
curl http://localhost:5001/api/signals/recommendations

# 4. Create order based on signal
curl -X POST http://localhost:5001/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USD",
    "side": "BUY",
    "quantity": 0.01,
    "order_type": "MARKET"
  }'

# 5. Monitor order status
curl http://localhost:5001/api/orders?limit=1
```

### Webhook Testing
```bash
# Generate signature
echo -n "webhook_payload" | openssl dgst -sha256 -hmac "your_secret"

# Send webhook
curl -X POST http://localhost:5001/webhook/tradingview \
  -H "Content-Type: application/json" \
  -H "X-Signature: sha256=generated_signature" \
  -d '{
    "symbol": "BTCUSD",
    "action": "BUY",
    "price": 50500
  }'
```

---

**Hinweis:** Alle Beispiele verwenden localhost. Für Produktionsumgebungen ersetzen Sie die URL entsprechend und verwenden Sie HTTPS.

