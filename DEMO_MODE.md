# 🎬 Demo Mode - Analytics Pipeline

## Overview

This repository is **demo mode** with **fictional data only**. All information is synthetic and safe for public presentations.

---

## 🔒 What's Fictional

### ✅ Safe for Public Viewing:
- **All customer data** - Names like "Cliente Demo 1"
- **All emails** - demo1@example.com, demo2@example.com
- **All phone numbers** - +569 XXXX XXXX (fictional)
- **All addresses** - "Calle Demo 123"
- **API credentials** - Non-functional demo keys
- **Revenue numbers** - Synthetic (~$258M CLP)
- **Order history** - 821 fictional orders from 2025
- **Product catalog** - 79 demo products
- **Analytics data** - Correlated with demo orders

### ⚠️ No Real Data
- **Zero real customer information**
- **Zero real API access**
- **Zero real transaction data**

---

## 📊 Demo Data Specifications

### Generated Data

| Metric | Value |
|--------|-------|
| **Orders** | 821 |
| **Revenue** | $258,128,850 CLP |
| **Avg Ticket** | $314,408 CLP |
| **Products** | 79 (4 categories) |
| **Customers** | 300 |
| **Time Period** | Jan 1 - Dec 31, 2025 |
| **GA Sessions** | ~1,820 records |
| **Facebook Records** | 364 daily metrics |

### Data Patterns

- ✅ **Seasonal variations** - Higher sales in Nov/Dec
- ✅ **Weekend patterns** - 20% boost on weekends
- ✅ **Realistic correlations** - GA sessions match orders
- ✅ **Geographic distribution** - 95% Chile, 5% others
- ✅ **Product categories** - Electronics, Home & Garden, Fashion, Sports

---

## 🚀 Quick Start

### Launch Demo

```bash
# Windows
LAUNCH.bat

# Linux/Mac
python -m streamlit run dashboard/app_woo_v2.py
```

Dashboard will open on: `http://localhost:8501`

### Reset Demo Data

Need fresh data for a new presentation?

```bash
# Windows
DEMO_RESET.bat

# Linux/Mac
python scripts/generate_demo_data.py
```

This regenerates all fictional data with new random variations.

---

## 🎯 Presentation Tips

###Key Features to Demonstrate

1. **Dashboard KPIs** (Main page)
   - Revenue trends
   - Order volume
   - Average ticket
   - Year-over-year comparisons

2. **Sales Analysis**
   - Daily sales charts with peaks
   - Product performance
   - Category breakdowns

3. **Customer Segmentation**
   - Geographic distribution
   - Customer lifetime value
   - Repeat purchase analysis

4. **Traffic Analytics**
   - Google Analytics integration
   - Channel performance
   - Conversion funnels

5. **Tax Exports**
   - IVA/F29 export functionality
   - Operación Renta helpers

### Demo Flow (5 minutes)

1. **[0:00-0:30]** Show KPI dashboard
   - "Here's the executive view with $258M in revenue"
   - Point out YoY comparison feature

2. **[0:30-1:30]** Sales analysis
   - "See how sales peak in December"
   - "This chart shows our top products"

3. **[1:30-2:30]** Traffic & conversion
   - "Analytics shows where customers come from"
   - "Most traffic is organic search"

4. **[2:30-3:30]** Customer insights
   - "95% of customers are from Chile"
   - "See repeat vs new customer patterns"

5. **[3:30-4:30]** Tax & compliance
   - "One-click export for SII declarations"
   - "Automatic IVA calculations"

6. **[4:30-5:00]** Q&A
   - Show data filtering
   - Demonstrate date range selection

---

## 🔄 Restoring Production Data

If you backed up production data, restore it:

### Windows
```batch
copy backups\pre-demo\*.db data\
copy .env.production .env
```

### Linux/Mac
```bash
cp backups/pre-demo/*.db data/
cp .env.production .env
```

---

## 📝 Important Notes

### For Demonstrations

- ✅ **Safe to show publicly** - No real data
- ✅ **Safe to screenshot** - Everything is fictional
- ✅ **Safe to screencast** - Record presentations freely

### For Development

- ⚠️ **Don't run ETL** - API credentials are fake
- ⚠️ **Don't expect real data** - Everything is generated
- ✅ **Test dashboard features** - All UI works perfectly

### Data Limitations

- **No real API connections** - WooCommerce/GA/FB keys are fake
- **Historical data only** - All data is from 2025
- **Static unless reset** - Data doesn't update automatically

---

## 🛠️ Technical Details

### Database Files

- `data/woocommerce.db` - Orders, products, customers
- `data/analytics.db` - Google Analytics sessions
- `data/facebook.db` - Facebook page insights
- `data/monitoring.db` - ETL execution logs

### Generation Script

**Location**: `scripts/generate_demo_data.py`

**What it does**:
- Creates 821 orders with realistic patterns
- Generates 79 products across 4 categories
- Creates 300 fictional customers
- Correlates GA data with WooCommerce sales
- Adds Facebook metrics

**Customization**:
Edit the script to change:
- Number of orders (`target_orders = 680`)
- Time period (`START_DATE`, `END_DATE`)
- Seasonal patterns (`SEASONAL_PATTERN`)
- Product categories (`PRODUCTS`)

---

## 🎓 Learning & Testing

This demo mode is perfect for:

- **Training new users** - No risk of breaking real data
- **Testing new features** - Safe sandbox environment
- **Client presentations** - Professional looking data
- **Development** - Test dashboard changes
- **Screenshots/videos** - Create marketing materials

---

## ⚡ Troubleshooting

### Dashboard won't load

```bash
# Check if dependencies are installed
pip install -r requirements.txt

# Verify databases exist
dir data\*.db  # Windows
ls data/*.db   # Linux/Mac
```

### No data showing

```bash
# Regenerate demo data
python scripts\generate_demo_data.py
```

### Want different data

Edit `scripts/generate_demo_data.py` and change:
- Product names
- Revenue amounts
- Number of orders
- Time periods

Then run `DEMO_RESET.bat`

---

## 📞 Support

**Technical Contact**: tomas.farias.e@ug.uchile.cl

**Response Time**: 24-48 hours

---

## 🎉 Ready to Present!

Your demo environment is fully configured with realistic fictional data. Launch the dashboard and showcase the Analytics Pipeline! 🚀
