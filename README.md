# Capacity Chemical — Product Revenue Dashboard

Interactive dashboard showing revenue by master formula, broken down by customer and pack size. Powered by live NetSuite data.

## Live Dashboard
**[View Dashboard](https://brey-dws-cto.github.io/cc-product-revenue-dashboard/Product_Revenue_Dashboard.html)**

## Features
- **Top 20 master formulas** displayed as donut charts with customer breakdown
- **Search any product** — type a formula code or name to filter (e.g., "CC2", "citric", "peroxide")
- **Click-through drill-down** — click any donut slice to see customer detail with pack size, price/lb, lbs, revenue
- **Revenue trend** — view monthly trends per product/customer
- **Date filtering** — preset ranges (YTD, Last 12 Months, etc.) or custom dates
- **Clickable stat cards** — click Total Revenue, Total Lbs, Customers, or Avg Revenue for summary charts

## Files
| File | Purpose |
|------|---------|
| `Product_Revenue_Dashboard.html` | Dashboard UI (Chart.js + vanilla JS) |
| `product_revenue_all.json` | All formula data (auto-refreshed daily) |
| `refresh_product_data.py` | Python script to pull data from NetSuite |
| `.github/workflows/refresh-data.yml` | GitHub Actions daily auto-refresh |

## Data Flow
```
NetSuite (SuiteQL REST API)
    → refresh_product_data.py (GitHub Actions, daily @ midnight MST)
    → product_revenue_all.json (committed to repo)
    → Product_Revenue_Dashboard.html (fetches JSON, renders charts)
    → GitHub Pages (served at public URL)
```

## Setup
1. Add NetSuite OAuth secrets to repo Settings → Secrets → Actions:
   - `NETSUITE_ACCOUNT_ID`
   - `NETSUITE_CONSUMER_KEY`
   - `NETSUITE_CONSUMER_SECRET`
   - `NETSUITE_TOKEN_ID`
   - `NETSUITE_TOKEN_SECRET`
2. Enable GitHub Pages (Settings → Pages → Deploy from branch: main)
3. Run the workflow manually to verify (Actions → Refresh Product Revenue Data → Run workflow)

## Top 20 Master Formulas (Fixed List)
Determined by 2025 full-year revenue analysis:

| # | Code | Formula |
|---|------|---------|
| 1 | CC1001 | Kanopy Clear Line |
| 2 | CC1047 | Premium Foaming Chloro-Alkali Cleaner |
| 3 | CC1017 | Kanopy Nano Mid |
| 4 | CC1022 | Hydrogen Peroxide 34%, Technical Grade |
| 5 | CC1024 | IPA 99% |
| 6 | CC1103 | Clear Line 1500 |
| 7 | CC1052 | Soil Guard SG |
| 8 | CC1018 | Kanopy Nano LC |
| 9 | CC6000 | Copper Sulfate 5% |
| 10 | CC1079 | No Foam S |
| 11 | CC5003 | TMB 471W 5% |
| 12 | CC2015 | Hydrogen Peroxide 34% FG |
| 13 | CC1085 | Hydrogen Peroxide 50% TG |
| 14 | CC0999 | Kanopy Clear Line Essential |
| 15 | CC1054 | CC1054 |
| 16 | CC1034 | Sulfuric Acid 93% |
| 17 | CC1107 | Causticlean Liquid |
| 18 | CC1106 | ATP Mineral Master |
| 19 | CC1157 | HYDRO SOLV |
| 20 | CC1262 | CaustiClean K (dry) |

---
*Prepared by Do What Solutions LLC*
