# User Guide - Analytics Pipeline

**For Business Users and Analysts**  
**Version**: 1.0 Generic Edition  
**Last Updated**: January 14, 2026  
**Support**: tomas.farias.e@ug.uchile.cl

---

## Welcome! 📊

This guide helps you use the Analytics Pipeline dashboard to analyze your e-commerce data. No technical knowledge required!

---

## Getting Started

### Accessing the Dashboard

1. **Open your web browser**
2. **Navigate to**: `http://localhost:8501` (if running locally)
   - Or use the URL provided by your system administrator
3. **Wait a moment** for the dashboard to load

### Dashboard Layout

The dashboard has three main sections:

```
┌─────────────────────────────────────────┐
│  📊 Analytics Pipeline                  │
│  [Sidebar: Filters & Settings]          │
├─────────────────────────────────────────┤
│                                         │
│  📈 Metrics Overview (cards)            │
│  • Total Revenue                        │
│  • Orders                               │
│  • Average Order Value                  │
│  • Conversion Rate                      │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  📊 Charts & Visualizations             │
│  • Revenue trends                       │
│  • Top products                         │
│  • Traffic sources                      │
│  • Geographic distribution              │
│                                         │
└─────────────────────────────────────────┘
```

---

## Using the Dashboard

### Filtering Data

All charts and metrics can be filtered using the **sidebar** (left side):

#### Date Range Filter

1. **Click** the date picker
2. **Select** start and end dates
3. **View** updated metrics instantly

**Common date ranges**:
- Last 7 days
- Last 30 days
- This month
- Last month
- Custom range

#### Comparison Mode

Enable **"Compare with Previous Period"** to see:
- Year-over-year comparison
- Month-over-month growth
- Performance trends

**Example**:
```
Current Period: January 2026
Selected Comparison: Previous Year
Result: Shows January 2025 data alongside January 2026
```

---

## Understanding Metrics

### Revenue Metrics

#### Total Revenue
The sum of all completed orders in the selected period.

**What it includes**:
- Product sales
- Shipping fees (if configured)

**What it excludes**:
- Refunds (shown separately)
- Pending/cancelled orders

#### Average Order Value (AOV)
The average amount spent per order.

**Formula**: Total Revenue ÷ Number of Orders

**Example**: $45,000 revenue from 150 orders = $300 AOV

**Why it matters**: Higher AOV means customers are buying more per transaction.

#### Revenue Growth
Percentage change compared to previous period.

**How to read**:
- 🟢 Green number = Growth (good!)
- 🔴 Red number = Decline (needs attention)
- ➖ Gray = No change

### Order Metrics

#### Total Orders
Number of completed orders in the period.

**Statuses included**:
- Completed
- Processing
- On-hold

**Statuses excluded**:
- Cancelled
- Refunded
- Failed

#### Conversion Rate
Percentage of visitors who made a purchase.

**Formula**: (Orders ÷ Visitors) × 100

**Example**: 50 orders from 2,000 visitors = 2.5% conversion rate

**Industry benchmark**: 2-3% is typical for e-commerce

### Traffic Metrics

#### Total Visitors
Number of unique visitors to your website.

**Source**: Google Analytics

**Note**: One person visiting multiple times = one unique visitor

#### Sessions
Total number of visits (one person can have multiple sessions).

**Example**: John visits Monday (1 session) and Friday (1 session) = 2 total sessions

---

## Using Charts

### Revenue Trend Chart

Shows daily, weekly, or monthly revenue over time.

**How to use**:
1. **Hover** over any point to see exact values
2. **Click** legend items to show/hide data series
3. **Zoom** by clicking and dragging

**What to look for**:
- 📈 Upward trends (growth)
- 📉 Sudden drops (investigate cause)
- 🔄 Seasonal patterns

### Top Products Chart

Displays best-selling products by revenue or quantity.

**Filters available**:
- Sort by revenue or quantity
- Filter by category
- Time period

**Actions**:
- Click product name to see details
- Export list for inventory planning

### Traffic Sources Chart

Shows where your customers came from.

**Common sources**:
- **Direct**: Typed URL or bookmark
- **Organic Search**: Google, Bing results
- **Social**: Facebook, Instagram, etc.
- **Referral**: Links from other websites
- **Email**: Email campaigns

**How to use this**:
- Identify most valuable channels
- Analyze marketing ROI
- Plan advertising spend

### Geographic Distribution Map

Visual map showing customer locations.

**Colors indicate**:
- Darker = More customers
- Lighter = Fewer customers

**Use cases**:
- Plan shipping strategies
- Target regional marketing
- Identify expansion opportunities

---

## Common Tasks

### Task 1: Check Today's Sales

1. **Open** dashboard
2. **Set date range** to "Today"
3. **View** Total Revenue card

**Quick check**:
- Look at the delta (↑ or ↓) compared to yesterday
- Green = better than yesterday
- Red = lower than yesterday

### Task 2: Compare This Month to Last Month

1. **Click** date picker
2. **Select** first and last day of current month
3. **Enable** "Compare with Previous Period"
4. **Choose** "Previous Period" as comparison

**You'll see**:
- Side-by-side metrics
- Growth percentages
- Trend visualizations

### Task 3: Find Best-Selling Products

1. **Scroll** to "Top Products" section
2. **Select** date range (default: last 30 days)
3. **Choose** sort option:
   - By Revenue (highest sales value)
   - By Quantity (most units sold)

**Export option**: Click "Download" to save as Excel

### Task 4: Analyze Traffic Sources

1. **Go to** "Traffic Sources" section
2. **View** pie chart showing breakdown
3. **Check** which channels drive most sales

**Action items**:
- If organic search is high: SEO is working
- If direct traffic is high: Strong brand recognition  
- If social is low: Opportunity to improve social media

### Task 5: Export Data

1. **Navigate** to section you want to export
2. **Click** "Download" or "Export" button
3. **Choose** format:
   - CSV (for Excel)
   - PDF (for reports)
   - Excel (formatted spreadsheet)

**Tip**: You can export individual charts or full dashboard data

---

## Understanding Alerts & Insights

### Automatic Insights

The dashboard analyzes your data and shows insights like:

#### 📊 Performance Alerts
```
🟢 Revenue is up 15% compared to last week
🔴 Conversion rate dropped 0.8% - check traffic quality
⚠️ 3 products are out of stock and receiving orders
```

#### 💡 Recommendations
```
💡 Your AOV is higher on weekends - consider weekend promotions
💡 Mobile traffic is 60% but mobile conversion is low - optimize mobile site
💡 Email campaigns drive 3x higher AOV than social traffic
```

### Alert Levels

| Icon | Meaning | Action |
|------|---------|--------|
| 🟢 | Positive trend | Keep doing what works |
| ⚠️ | Needs attention | Review and adjust |
| 🔴 | Issue detected | Take action soon |
| 💡 | Opportunity | Consider implementing |

---

## Troubleshooting

### Dashboard Shows "No Data"

**Possible causes**:
1. No orders in selected date range
2. Data not yet extracted
3. Database connection issue

**Solutions**:
1. Try a different date range
2. Wait a few minutes and refresh
3. Contact technical support

### Charts Not Loading

**Try**:
1. **Refresh** the page (F5)
2. **Clear browser cache**: Ctrl+Shift+Delete
3. **Try different browser** (Chrome recommended)

### Data Looks Wrong

**Check**:
1. Date filter settings
2. Status filter (are refunds excluded?)
3. Currency conversion settings

**Still wrong?** Contact support with:
- What metric looks wrong
- What you expect vs what you see
- Screenshot of the issue

---

## Tips & Best Practices

### 📅 Regular Check-in Routine

**Daily** (5 minutes):
- Check today's revenue
- Review new orders
- Look for anomalies

**Weekly** (15 minutes):
- Compare to last week
- Review top products
- Check traffic sources

**Monthly** (30 minutes):
- Full month comparison
- Analyze trends
- Export reports for stakeholders

### 🎯 Goal Setting

Use the dashboard to track goals:

1. **Set baseline**: Review last month's metrics
2. **Define target**: E.g., "Increase revenue by 10%"
3. **Monitor weekly**: Use comparison mode
4. **Adjust strategy**: Based on what's working

### 📈 Seasonal Analysis

**Compare same month last year**:
- Accounts for seasonal trends
- More accurate growth measurement
- Better forecasting

**Example**:
```
December 2025 vs December 2024
(Not December 2025 vs November 2025)
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Refresh dashboard |
| `Ctrl + F` | Search on page |
| `Ctrl + P` | Print/Save as PDF |
| `Ctrl + Click` | Open in new tab |

---

## Glossary

**AOV**: Average Order Value - average amount per order  
**Conversion Rate**: Percentage of visitors who buy  
**CTR**: Click-Through Rate - percentage who click  
**GMV**: Gross Merchandise Value - total sales value  
**ROI**: Return on Investment  
**SKU**: Stock Keeping Unit - product identifier  
**UTM**: Tracking parameters for campaign analytics

---

## Getting Help

### Self-Service

1. **Check this guide** for how-to instructions
2. **Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for common issues
3. **Watch dashboard tutorial video** (if available)

### Contact Support

**Email**: tomas.farias.e@ug.uchile.cl

**Include**:
- Screenshot of the issue
- What you were trying to do
- Date range you were viewing
- Browser you're using

**Response time**: Usually within 24 hours

---

## Appendix: Sample Reports

### Monthly Executive Summary

**Include**:
- Total revenue vs target
- Order count and AOV
- Top 10 products
- Traffic source breakdown
- Key insights and recommendations

**Export as**: PDF from dashboard

### Weekly Performance Report

**Include**:
- Week-over-week comparison
- Daily revenue trend
- Conversion rate changes
- Alert summary

**Frequency**: Every Monday morning

### Product Performance Report

**Include**:
- Sales by product category
- Stock status
- Revenue per product
- Slow-moving inventory

**Use for**: Inventory planning

---

**Need more help?** Contact: tomas.farias.e@ug.uchile.cl
