# Yahoo Finance FastAPI

A FastAPI-based API to fetch stock financial data, statistics, and company profile from Yahoo Finance.

---

# Features

- Fetch Income Statement, Balance Sheet, Cash Flow
- Returns latest 4 financial years (sorted)
- Company Profile (Sector, Industry, Employees)
- Summary Data (Price, Volume, Market Cap, etc.)
- Financial Highlights & Key Statistics
- Handles invalid stock symbols
- Clean JSON output (no NaN errors)

---

# Tech Stack

- FastAPI
- Uvicorn
- yfinance
- pandas
- numpy

---

# Installation

```bash
git clone https://github.com/your-username/yahoo-finance-api.git
cd yahoo-finance-api

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt