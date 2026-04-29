from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
import numpy as np
import math
from datetime import datetime

app = FastAPI(title="Yahoo Finance API")


def make_json_safe(obj):
    if obj is None:
        return None

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.floating,)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)

    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")

    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d")

    if isinstance(obj, dict):
        return {key: make_json_safe(value) for key, value in obj.items()}

    if isinstance(obj, list):
        return [make_json_safe(item) for item in obj]

    return obj


def clean_dataframe(df: pd.DataFrame):
    if df is None or df.empty:
        return []

    df = df.T
    df.reset_index(inplace=True)
    df.rename(columns={"index": "financial_year"}, inplace=True)

    df["financial_year"] = df["financial_year"].astype(str)

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.replace({np.nan: None})

    records = df.to_dict(orient="records")
    return make_json_safe(records)


def convert_timestamp(value):
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except:
        pass

    try:
        return datetime.fromtimestamp(value).strftime("%b %d, %Y")
    except:
        return value
def format_financials(df: pd.DataFrame):
    if df is None or df.empty:
        return {}

    # Keep latest 4 columns
    df = df.iloc[:, :4]

    # Sort in increasing order
    df = df.reindex(sorted(df.columns), axis=1)

    # Format dates (remove time)
    dates = [col.strftime("%Y-%m-%d") for col in df.columns]

    result = {
        "dates": dates
    }

    for index, row in df.iterrows():
        values = []
        for val in row:
            if pd.isna(val):
                values.append(None)
            else:
                values.append(val)

        result[index] = values

    return make_json_safe(result)

@app.get("/")
def home():
    return {
        "message": "Yahoo Finance FastAPI running",
        "example": "/financials/AAPL"
    }


@app.get("/financials/{ticker_symbol}")
def get_financial_data(ticker_symbol: str):
    try:
        ticker_symbol = ticker_symbol.upper()
        ticker = yf.Ticker(ticker_symbol)

        # ✅ Validate stock exists
        hist = ticker.history(period="1d")

        if hist.empty:
            return {
                "status": "error",
                "message": f"Stock '{ticker_symbol}' not found"
            }

        info = ticker.info

        if not info:
            raise HTTPException(status_code=404, detail="Ticker not found")

        profile = {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "full_time_employees": info.get("fullTimeEmployees")
        }

        summary = {
            "previous_close": info.get("previousClose"),
            "open": info.get("open"),
            "bid": f"{info.get('bid')} x {info.get('bidSize')}",
            "ask": f"{info.get('ask')} x {info.get('askSize')}",
            "days_range": f"{info.get('dayLow')} - {info.get('dayHigh')}",
            "fifty_two_week_range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
            "volume": info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "market_cap_intraday": info.get("marketCap"),
            "beta_5y_monthly": info.get("beta"),
            "pe_ratio_ttm": info.get("trailingPE"),
            "eps_ttm": info.get("trailingEps"),
            "earnings_date": convert_timestamp(info.get("earningsTimestamp")),
            "forward_dividend": info.get("dividendRate"),
            "forward_dividend_yield": info.get("dividendYield"),
            "ex_dividend_date": convert_timestamp(info.get("exDividendDate")),
            "one_year_target_est": info.get("targetMeanPrice")
        }

        statistics = {
    "financial_highlights": {
        "fiscal_year": {
            "fiscal_year_ends": convert_timestamp(info.get("lastFiscalYearEnd")),
            "most_recent_quarter": convert_timestamp(info.get("mostRecentQuarter"))
        },
        "profitability": {
            "profit_margin": info.get("profitMargins"),
            "operating_margin_ttm": info.get("operatingMargins")
        },
        "management_effectiveness": {
            "return_on_assets_ttm": info.get("returnOnAssets"),
            "return_on_equity_ttm": info.get("returnOnEquity")
        },
        "income_statement": {
            "revenue_ttm": info.get("totalRevenue"),
            "revenue_per_share_ttm": info.get("revenuePerShare"),
            "quarterly_revenue_growth_yoy": info.get("revenueGrowth"),
            "gross_profit_ttm": info.get("grossProfits"),
            "ebitda": info.get("ebitda"),
            "net_income_to_common_ttm": info.get("netIncomeToCommon"),
            "diluted_eps_ttm": info.get("trailingEps"),
            "quarterly_earnings_growth_yoy": info.get("earningsGrowth")
        },
        "balance_sheet": {
            "total_cash_mrq": info.get("totalCash"),
            "total_cash_per_share_mrq": info.get("totalCashPerShare"),
            "total_debt_mrq": info.get("totalDebt"),
            "total_debt_equity_mrq": info.get("debtToEquity"),
            "current_ratio_mrq": info.get("currentRatio"),
            "book_value_per_share_mrq": info.get("bookValue")
        },
        "cash_flow_statement": {
            "operating_cash_flow_ttm": info.get("operatingCashflow"),
            "levered_free_cash_flow_ttm": info.get("freeCashflow")
        }
    },

    "trading_information": {
        "stock_price_history": {
            "beta_5y_monthly": info.get("beta"),
            "fifty_two_week_change": info.get("52WeekChange"),
            "sp_500_52_week_change": info.get("SandP52WeekChange"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_day_moving_average": info.get("fiftyDayAverage"),
            "two_hundred_day_moving_average": info.get("twoHundredDayAverage")
        },
        "share_statistics": {
            "avg_vol_3_month": info.get("averageVolume"),
            "avg_vol_10_day": info.get("averageVolume10days"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "implied_shares_outstanding": info.get("impliedSharesOutstanding"),
            "float": info.get("floatShares"),
            "held_by_insiders": info.get("heldPercentInsiders"),
            "held_by_institutions": info.get("heldPercentInstitutions"),
            "shares_short": info.get("sharesShort"),
            "short_ratio": info.get("shortRatio"),
            "short_percent_of_float": info.get("shortPercentOfFloat"),
            "short_percent_of_shares_outstanding": info.get("sharesPercentSharesOut"),
            "shares_short_prior_month": info.get("sharesShortPriorMonth")
        },
        "dividends_and_splits": {
            "forward_annual_dividend_rate": info.get("dividendRate"),
            "forward_annual_dividend_yield": info.get("dividendYield"),
            "trailing_annual_dividend_rate": info.get("trailingAnnualDividendRate"),
            "trailing_annual_dividend_yield": info.get("trailingAnnualDividendYield"),
            "five_year_average_dividend_yield": info.get("fiveYearAvgDividendYield"),
            "payout_ratio": info.get("payoutRatio"),
            "dividend_date": convert_timestamp(info.get("dividendDate")),
            "ex_dividend_date": convert_timestamp(info.get("exDividendDate")),
            "last_split_factor": info.get("lastSplitFactor"),
            "last_split_date": convert_timestamp(info.get("lastSplitDate"))
        }
    }
}
        response_data = {
            "ticker": ticker_symbol,
            "profile": profile,
            "summary": summary,
            "key_statistics":statistics,
            "financials": {
                "income_statement": format_financials(ticker.financials),
                "balance_sheet": format_financials(ticker.balance_sheet),
                "cash_flow": format_financials(ticker.cashflow)
            }
        }

        return JSONResponse(content=make_json_safe(response_data))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))