import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from components.stock_engine import (
    get_stock_data, get_current_price,
    get_moving_average, get_stock_info
)
from components.news_engine import (
    get_news_with_sentiment, get_risk_indicator, get_news
)
from components.simulator import run_simulation, buyer_request, merchant_offer

# ── Page Configuration ─────────────────────────────
st.set_page_config(
    page_title="UCP Stock Analysis Platform",
    page_icon="📈",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0a0e1a;
        color: #e0e6f0;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1526;
        border-right: 1px solid #1e3a5f;
    }
    [data-testid="metric-container"] {
        background-color: #0d1e35;
        border: 1px solid #1a3a5c;
        border-radius: 10px;
        padding: 15px;
    }
    .stButton > button {
        background-color: #1a4a8a;
        color: white;
        border: 1px solid #2a6abf;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #2a6abf;
        border-color: #4a8adf;
    }
    h1, h2, h3 { color: #4a9eff; }
    hr { border-color: #1e3a5f; }
    .stTextInput > div > div > input {
        background-color: #0d1e35;
        color: #e0e6f0;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
    }
    .stSelectbox > div > div {
        background-color: #0d1e35;
        color: #e0e6f0;
        border: 1px solid #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)

# ── Stock List ─────────────────────────────────────
stock_list = {
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Google (GOOGL)": "GOOGL",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Saudi Aramco (2222.SR)": "2222.SR",
    "SABIC (2010.SR)": "2010.SR",
    "STC (7010.SR)": "7010.SR",
    "NVIDIA (NVDA)": "NVDA",
    "Meta (META)": "META",
}

# ── Sidebar ────────────────────────────────────────
st.sidebar.markdown("## 🔍 Search Stock")
search = st.sidebar.text_input("Search by name or symbol").upper()
filtered = {k: v for k, v in stock_list.items() if search in k.upper()}

if filtered:
    selected = st.sidebar.selectbox("Select Stock", list(filtered.keys()))
    symbol = filtered[selected]
else:
    st.sidebar.warning("No stocks found")
    symbol = "AAPL"

period = st.sidebar.selectbox("Select Period", ["7d", "30d", "90d", "180d", "1y"])
forecast_days = st.sidebar.slider("Forecast Days", min_value=3, max_value=30, value=7)
st.sidebar.markdown("---")
analyze = st.sidebar.button("📊 Analyze")

# ── Session State ──────────────────────────────────
if "order_result" not in st.session_state:
    st.session_state.order_result = None
if "sim_result" not in st.session_state:
    st.session_state.sim_result = None
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "symbol_analyzed" not in st.session_state:
    st.session_state.symbol_analyzed = None

if analyze:
    st.session_state.analyzed = True
    st.session_state.symbol_analyzed = symbol
    st.session_state.order_result = None
    st.session_state.sim_result = None

# ── Title ──────────────────────────────────────────
st.markdown("""
    <h1 style='text-align: center; color: #4a9eff;'>
        📈 UCP Stock Analysis Platform
    </h1>
    <p style='text-align: center; color: #7a9abf;'>
        Real-time stock analysis powered by AI & UCP Protocol
    </p>
""", unsafe_allow_html=True)
st.markdown("---")

if st.session_state.analyzed:
    symbol = st.session_state.symbol_analyzed

    # ── Section 1: Company Info ────────────────────
    st.markdown("### 🏢 Company Information")
    info = get_stock_info(symbol)
    price = get_current_price(symbol)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏷️ Company", info["name"])
    col2.metric("🏭 Sector", info["sector"])
    col3.metric("🌍 Country", info["country"])
    col4.metric("💰 Current Price", f"${price}")
    st.markdown("---")

    # ── Section 2: Price Chart ─────────────────────
    st.markdown("### 📊 Price Chart & Moving Average")
    df = get_moving_average(symbol)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Close"],
        name="Close Price",
        line=dict(color="#4a9eff", width=2),
        fill='tozeroy',
        fillcolor='rgba(74, 158, 255, 0.05)'
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA"],
        name="Moving Average",
        line=dict(color="#ff9f43", width=2, dash="dash")
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1526",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        legend=dict(bgcolor="#0d1526"),
        font=dict(color="#e0e6f0")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    # ── Section 3: Price Forecast ──────────────────
    st.markdown(f"### 🔮 Price Forecast — Next {forecast_days} Days")

    df_forecast = get_stock_data(symbol, period="90d")
    df_forecast = df_forecast.dropna()
    df_forecast["Day"] = np.arange(len(df_forecast))

    X = df_forecast[["Day"]]
    y = df_forecast["Close"]
    model = LinearRegression()
    model.fit(X, y)

    last_day = df_forecast["Day"].iloc[-1]
    future_days = np.arange(last_day + 1, last_day + forecast_days + 1).reshape(-1, 1)
    future_prices = model.predict(future_days)

    last_date = pd.to_datetime(df_forecast["Date"].iloc[-1])
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_forecast["Date"], y=df_forecast["Close"],
        name="Historical Price",
        line=dict(color="#4a9eff", width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=future_dates, y=future_prices,
        name="Forecasted Price",
        line=dict(color="#00d2a0", width=2, dash="dot")
    ))
    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1526",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        font=dict(color="#e0e6f0")
    )
    st.plotly_chart(fig2, use_container_width=True)

    forecast_df = pd.DataFrame({
        "Date": future_dates.strftime("%Y-%m-%d"),
        "Forecasted Price ($)": [round(p, 2) for p in future_prices]
    })
    st.dataframe(forecast_df, use_container_width=True)
    st.markdown("---")

    # ── Section 4: News & Risk ─────────────────────
    st.markdown("### 🌍 Global News & Geopolitical Risk")
    articles = get_news_with_sentiment(symbol)
    raw_articles = get_news(symbol)
    risk, avg_score = get_risk_indicator(raw_articles)

    risk_col1, risk_col2 = st.columns(2)
    risk_col1.markdown(f"#### Risk Indicator: {risk}")
    risk_col2.markdown(f"#### Sentiment Score: `{round(avg_score, 3)}`")
    st.markdown("---")

    for article in articles[:5]:
        sentiment = article["sentiment"]
        color = "🟢" if sentiment == "Positive" else "🔴" if sentiment == "Negative" else "⚪"
        st.markdown(f"{color} **{article['title']}**")
        st.markdown(f"Sentiment: `{sentiment}` | Score: `{article['score']}` | [Read More]({article['url']})")
        st.markdown("---")

    # ── Section 5: UCP Trading ─────────────────────
    st.markdown("### ⚙️ UCP Protocol — Place Order")

    col1, col2 = st.columns(2)
    with col1:
        buyer_name = st.text_input("Buyer Name", placeholder="Enter your name")
        quantity = st.number_input("Quantity", min_value=1, value=10)
    with col2:
        order_price = st.number_input("Price per Share", min_value=0.01, value=float(price))

    col_buy, col_sim = st.columns(2)

    with col_buy:
        if st.button("🛒 Place Order"):
            merchant_offer(symbol, order_price)
            order, invoice = buyer_request(buyer_name, symbol, quantity, order_price)
            st.session_state.order_result = (order, invoice)

        if st.session_state.order_result:
            order, invoice = st.session_state.order_result
            if order["status"] == "APPROVED":
                st.success(f"✅ Order Approved! Total: ${invoice['total']}")
                st.json(invoice)
            else:
                st.error(f"❌ Order Rejected: {order.get('reason')}")

    with col_sim:
        if st.button("🤖 Run Simulation"):
            order, invoice = run_simulation(symbol, order_price)
            st.session_state.sim_result = (order, invoice)

        if st.session_state.sim_result:
            order, invoice = st.session_state.sim_result
            if invoice:
                st.success(f"✅ Simulation Complete! Invoice: {invoice['invoice_id']}")
                st.json(invoice)

    st.markdown("---")

    # ── Section 6: Audit Log ───────────────────────
    st.markdown("### 📋 Audit Log")
    from components.ucp_engine import get_logs
    logs = get_logs()
    if logs:
        for log in reversed(logs[-10:]):
            st.json(log)
    else:
        st.info("No transactions recorded yet.")