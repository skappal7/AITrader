import streamlit as st
import yfinance as yf
from alpaca_trade_api import REST
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize APIs
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url='https://paper-api.alpaca.markets')
openai.api_key = OPENAI_API_KEY

# Functions to fetch data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1y")

def get_alpaca_data(ticker, start, end):
    barset = alpaca.get_barset(ticker, 'day', start=start, end=end)
    return barset[ticker].df

def upload_historical_data():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        return data
    return None

# Technical Analysis Functions
def calculate_technical_indicators(df):
    df['SMA'] = df['Close'].rolling(window=20).mean()
    df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()
    return df

def plot_stock_data(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='market data'))
    fig.update_layout(title=ticker, yaxis_title='Stock Price (USD)')
    st.plotly_chart(fig)

# ChatGPT Integration
def get_recommendation(ticker, df):
    prompt = f"Provide a detailed analysis for {ticker} based on the following data:\n\n{df.tail(20).to_string()}"
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=500)
    return response.choices[0].text.strip()

# Streamlit App
st.title("S&P 500 Stock Analyst App")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home", "Technical Analysis", "Historical Data", "Recommendations"])

if page == "Home":
    st.header("Welcome to the S&P 500 Stock Analyst App")

elif page == "Technical Analysis":
    st.header("Technical Analysis Dashboard")
    ticker = st.text_input("Enter a stock ticker (e.g., AAPL)")
    if ticker:
        df = get_stock_data(ticker)
        df = calculate_technical_indicators(df)
        plot_stock_data(df, ticker)

elif page == "Historical Data":
    st.header("Upload Historical Put/Call Data")
    data = upload_historical_data()
    if data is not None:
        st.write(data.head())

elif page == "Recommendations":
    st.header("Buy/Sell/Hold Recommendations")
    ticker = st.text_input("Enter a stock ticker (e.g., AAPL)")
    if ticker:
        df = get_stock_data(ticker)
        recommendation = get_recommendation(ticker, df)
        st.write(recommendation)
