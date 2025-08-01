import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Streamlit Page Configuration
st.set_page_config(page_title="📊 STOCK.X", layout="wide")

# Title
st.markdown("""
<h1 style='text-align: center;'>📈 STOCK.X</h1>
<h4 style='text-align: center; color: gray;'>Choose and grow high</h4>
""", unsafe_allow_html=True)

# Sidebar Inputs
symbols = st.sidebar.multiselect(
    "Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC", "TCS.NS", "RELIANCE.NS"],
    default=["AAPL"]
)

# Time Range Selector
range_option = st.sidebar.selectbox("Select Time Range", ["Today", "1M", "6M", "1Y", "3Y", "5Y", "Max"], index=2)

end_date = datetime.today()
if range_option == "Today":
    start_date = end_date - timedelta(days=1)
elif range_option == "1M":
    start_date = end_date - timedelta(days=30)
elif range_option == "6M":
    start_date = end_date - timedelta(days=182)
elif range_option == "1Y":
    start_date = end_date - timedelta(days=365)
elif range_option == "3Y":
    start_date = end_date - timedelta(days=1095)
elif range_option == "5Y":
    start_date = end_date - timedelta(days=1825)
else:
    start_date = datetime(2000, 1, 1)

# Show NIFTY 50 and SENSEX Prices Below the Stock Selector
st.sidebar.markdown("---")
st.sidebar.markdown("### 🇮🇳 Indian Market Indices")

try:
    nifty = yf.Ticker("^NSEI").history(period="1d")
    sensex = yf.Ticker("^BSESN").history(period="1d")
    st.sidebar.metric("NIFTY 50", f"₹{nifty['Close'].iloc[-1]:,.2f}", f"{nifty['Close'].pct_change().iloc[-1]*100:.2f}%")
    st.sidebar.metric("SENSEX", f"₹{sensex['Close'].iloc[-1]:,.2f}", f"{sensex['Close'].pct_change().iloc[-1]*100:.2f}%")
except:
    st.sidebar.error("Failed to fetch NIFTY/SENSEX data")

# Watchlist
st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Watchlist")
watchlist = st.sidebar.text_input("Enter symbols separated by comma (e.g., AAPL, TCS.NS)")
if watchlist:
    for symbol in [s.strip().upper() for s in watchlist.split(",")]:
        try:
            data = yf.Ticker(symbol).history(period="1d")
            st.sidebar.metric(symbol, f"₹{data['Close'].iloc[-1]:,.2f}", f"{data['Close'].pct_change().iloc[-1]*100:.2f}%")
        except:
            st.sidebar.warning(f"Could not load {symbol}")

# Main Content
if symbols:
    df = yf.download(symbols, start=start_date, end=end_date)
    df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df.columns]
    df.reset_index(inplace=True)

    st.subheader("📋 Market Overview")
    st.dataframe(df.head(), use_container_width=True)
    st.download_button("📥 Download Data", df.to_csv(index=False).encode(), "stock_data.csv", "text/csv")

    # Closing Price Trend
    st.subheader("📈 Price Trend")
    fig1 = px.line()
    for symbol in symbols:
        if f"Close_{symbol}" in df.columns:
            fig1.add_scatter(x=df['Date'], y=df[f"Close_{symbol}"], mode='lines', name=symbol)
    fig1.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig1, use_container_width=True)

    # Moving Average
    st.subheader("📉 Moving Average (20-day)")
    fig_ma = px.line()
    for symbol in symbols:
        if f"Close_{symbol}" in df.columns:
            df[f"MA20_{symbol}"] = df[f"Close_{symbol}"].rolling(window=20).mean()
            fig_ma.add_scatter(x=df['Date'], y=df[f"MA20_{symbol}"], mode='lines', name=f"{symbol} MA20")
    fig_ma.update_layout(title="20-Day Moving Average", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig_ma, use_container_width=True)

    # Volume Traded
    st.subheader("📊 Volume Traded")
    fig2 = px.area()
    for symbol in symbols:
        if f"Volume_{symbol}" in df.columns:
            fig2.add_scatter(x=df['Date'], y=df[f"Volume_{symbol}"], mode='lines', name=symbol, stackgroup='one')
    fig2.update_layout(title="Daily Volume Traded", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig2, use_container_width=True)

    # Buy / Sell Buttons
    cols = st.columns(len(symbols))
    for i, symbol in enumerate(symbols):
        with cols[i]:
            st.markdown(f"<button style='background-color:#28a745;color:white;padding:8px;border:none;border-radius:5px;width:100%;'>🟢 Buy {symbol}</button>", unsafe_allow_html=True)
            st.markdown(f"<button style='background-color:#dc3545;color:white;padding:8px;border:none;border-radius:5px;width:100%;'>🔴 Sell {symbol}</button>", unsafe_allow_html=True)

    # Company Info + Fundamental Analysis
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        st.markdown(f"## 🔎 {symbol} - {info.get('shortName', 'N/A')}")
        summary = info.get('longBusinessSummary', 'N/A')
        st.markdown(f"*About:* {summary[:200]}{'...' if len(summary) > 200 else ''}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Key Metrics")
            st.markdown(f"- *Sector:* {info.get('sector', 'N/A')}")
            st.markdown(f"- *Market Cap:* {info.get('marketCap', 'N/A'):,}")
            st.markdown(f"- *P/E Ratio:* {info.get('trailingPE', 'N/A')}")
            st.markdown(f"- *EPS:* {info.get('trailingEps', 'N/A')}")
        with col2:
            st.markdown("### More Insights")
            st.markdown(f"- *Dividend Yield:* {info.get('dividendYield', 'N/A')}")
            st.markdown(f"- *52W High:* {info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.markdown(f"- *52W Low:* {info.get('fiftyTwoWeekLow', 'N/A')}")
            st.markdown(f"- *Beta:* {info.get('beta', 'N/A')}")
else:
    st.warning("👈 Please select at least one stock symbol to view data.")
