# 🚀 AI Agent Quick Start

Your AI agent is ready to use! It can understand natural language commands and interact with both Shopify and Google Sheets.

## 🎯 Quick Commands

### From Command Line

```bash
# Sync orders from Shopify to Google Sheets
python src/ai_agent.py "sync orders"

# Get revenue information
python src/ai_agent.py "show revenue"

# Get orders summary
python src/ai_agent.py "orders summary"

# Get product sales breakdown
python src/ai_agent.py "product sales"

# Get profit breakdown
python src/ai_agent.py "profit breakdown"

# Backup PSL values
python src/ai_agent.py "backup PSL"

# Restore PSL values
python src/ai_agent.py "restore PSL"
```

### From Web Interface

1. **Start the server:**
   ```bash
   python run_app.py
   ```

2. **Open the web interface:**
   - Open `test_agent.html` in your browser
   - Or visit: `http://localhost:8000/api/agent/capabilities`

3. **Use the interface:**
   - Click quick command buttons
   - Or type your own command in the input box
   - Click "Execute" or press Enter

### From API

```bash
# Process a command
curl -X POST "http://localhost:8000/api/agent/command" \
  -H "Content-Type: application/json" \
  -d '{"command": "sync orders"}'

# Get available commands
curl "http://localhost:8000/api/agent/capabilities"

# Check agent health
curl "http://localhost:8000/api/agent/health"
```

## 📋 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `sync orders` | Sync orders from Shopify to Google Sheets | `"sync orders from shopify"` |
| `show revenue` | Get total revenue and sales info | `"show me total revenue"` |
| `orders summary` | Get summary of orders | `"give me orders summary"` |
| `product sales` | Get product sales breakdown | `"what products sold the most?"` |
| `profit breakdown` | Get profit analysis | `"show me profit breakdown"` |
| `backup PSL` | Backup PSL values | `"backup PSL values"` |
| `restore PSL` | Restore PSL values | `"restore PSL values"` |
| `customer insights` | Get customer purchase insights | `"show me customer insights"` |

## 🎨 Example Responses

### Revenue Response
```json
{
  "success": true,
  "message": "Revenue information retrieved",
  "data": {
    "revenue": {
      "total_revenue": "$353.26",
      "net_profit": "$34.50",
      "units_sold": "26",
      "shopify_payout": "$337.02"
    }
  }
}
```

### Orders Summary Response
```json
{
  "success": true,
  "message": "Orders summary retrieved",
  "data": {
    "total_orders": 26,
    "total_value": 353.26,
    "status_breakdown": {
      "paid": 24,
      "pending": 2
    }
  }
}
```

## 🔧 Next Steps

1. **Test the agent:** Try running a few commands
2. **Integrate into your workflow:** Use the API endpoints in your applications
3. **Customize:** Add new commands in `src/ai_agent.py`
4. **Expand:** Add more capabilities like email notifications, scheduled tasks, etc.

---

**Need help?** Check `AI_AGENT_GUIDE.md` for detailed documentation!
