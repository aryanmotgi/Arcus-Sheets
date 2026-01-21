# 🤖 AI Agent for Google Sheets & Shopify

Your AI agent can understand natural language commands and automatically sync data from Shopify to Google Sheets, provide insights, and update information.

## 🚀 Quick Start

### Start the Server

```bash
python run_app.py
```

The API will be available at: `http://localhost:8000`

### Use the Agent via API

#### Process a Command

```bash
POST http://localhost:8000/api/agent/command
Content-Type: application/json

{
  "command": "sync orders from shopify"
}
```

#### Get Available Commands

```bash
GET http://localhost:8000/api/agent/capabilities
```

## 📝 Available Commands

### 1. **Sync Orders**
Sync orders from Shopify to Google Sheets

**Command examples:**
- `"sync orders"`
- `"update orders from shopify"`
- `"refresh orders sheet"`

**What it does:**
- Fetches all orders from Shopify
- Processes and formats the data
- Updates the Orders sheet in Google Sheets
- Preserves your PSL values automatically

---

### 2. **Revenue Information**
Get total revenue and sales breakdown

**Command examples:**
- `"show revenue"`
- `"total sales"`
- `"how much revenue?"`

**What it returns:**
- Total Revenue
- Net Profit
- Units Sold
- Shopify Payout

---

### 3. **Orders Summary**
Get summary of orders from Shopify

**Command examples:**
- `"orders summary"`
- `"list orders"`
- `"how many orders?"`

**What it returns:**
- Total number of orders
- Total order value
- Breakdown by status (Paid, Pending, etc.)

---

### 4. **Product Sales**
Get product sales breakdown

**Command examples:**
- `"product sales"`
- `"what products sold?"`
- `"items sold"`

**What it returns:**
- Sales per product
- Quantities sold
- Revenue per product

---

### 5. **Profit Breakdown**
Get detailed profit analysis

**Command examples:**
- `"profit breakdown"`
- `"show profit"`
- `"what's my profit?"`

**What it returns:**
- Total Revenue
- Total Product Costs
- Total Costs (fixed)
- Net Profit
- Profit Per Shirt

---

### 6. **PSL Backup**
Backup your PSL (Private Shipping Label) values

**Command examples:**
- `"backup PSL"`
- `"save PSL values"`

**What it does:**
- Reads all PSL values from Google Sheets
- Saves them to `config/psl_backup.json`

---

### 7. **PSL Restore**
Restore PSL values from backup

**Command examples:**
- `"restore PSL"`
- `"restore PSL values"`

**What it does:**
- Reads backup file
- Restores all PSL values to Google Sheets

---

### 8. **Customer Insights**
Get customer purchase insights

**Command examples:**
- `"customer insights"`
- `"top customers"`
- `"who bought the most?"`

**What it returns:**
- Total customers
- Top 10 customers by spending
- Customer order counts

---

## 💻 Command Line Usage

You can also use the agent directly from command line:

```bash
# Sync orders
python src/ai_agent.py "sync orders"

# Get revenue
python src/ai_agent.py "show revenue"

# Product sales
python src/ai_agent.py "product sales"

# Profit breakdown
python src/ai_agent.py "profit breakdown"
```

## 🌐 Web Interface (Future)

You can create a simple web interface using the API endpoints:

```javascript
// Example: Sync orders
fetch('http://localhost:8000/api/agent/command', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ command: 'sync orders' })
})
.then(r => r.json())
.then(data => console.log(data));
```

## 📊 Example Responses

### Sync Orders Response
```json
{
  "success": true,
  "message": "Orders synced successfully!",
  "command": "sync orders",
  "data": {
    "status": "success",
    "message": "Orders synced successfully",
    "timestamp": "2026-01-19T16:30:00"
  }
}
```

### Revenue Response
```json
{
  "success": true,
  "message": "Revenue information retrieved",
  "command": "show revenue",
  "data": {
    "revenue": {
      "total_revenue": "$520.00",
      "net_profit": "$210.50",
      "units_sold": 26,
      "shopify_payout": "$485.92"
    },
    "timestamp": "2026-01-19T16:30:00"
  }
}
```

## 🔧 Advanced: Add Custom Commands

You can extend the agent by adding new commands in `src/ai_agent.py`:

```python
# Add to available_commands
'my_custom_command': self._my_custom_function,

# Implement the function
def _my_custom_function(self) -> Dict:
    # Your custom logic here
    return {'status': 'success'}
```

## 📱 Integration Ideas

1. **Slack Bot**: Connect to Slack and use commands like `/sync-orders`
2. **Discord Bot**: Similar to Slack integration
3. **Web Dashboard**: Create a simple UI with buttons for common commands
4. **Google Apps Script**: Integrate directly into Google Sheets
5. **Scheduled Tasks**: Auto-sync daily/weekly

---

**Need help?** Try: `GET /api/agent/capabilities` to see all available commands!
