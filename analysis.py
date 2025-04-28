import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os


def calculate_technical_indicators(hist):
    """Calculate technical indicators for stock analysis"""
    hist['MA20'] = hist['Close'].rolling(window=20).mean()
    hist['MA50'] = hist['Close'].rolling(window=50).mean()
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    hist['RSI'] = 100 - (100 / (1 + rs))
    hist['EMA12'] = hist['Close'].ewm(span=12, adjust=False).mean()
    hist['EMA26'] = hist['Close'].ewm(span=26, adjust=False).mean()
    hist['MACD'] = hist['EMA12'] - hist['EMA26']
    hist['Signal_Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()
    hist['BB_middle'] = hist['Close'].rolling(window=20).mean()
    hist['BB_upper'] = hist['BB_middle'] + 2 * hist['Close'].rolling(window=20).std()
    hist['BB_lower'] = hist['BB_middle'] - 2 * hist['Close'].rolling(window=20).std()
    high_low = hist['High'] - hist['Low']
    high_close = np.abs(hist['High'] - hist['Close'].shift())
    low_close = np.abs(hist['Low'] - hist['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    hist['ATR'] = true_range.rolling(14).mean()
    return hist

def plot_technical_analysis(hist, ticker):
    """Create technical analysis charts"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), height_ratios=[3, 1, 1])
    ax1.plot(hist.index, hist['Close'], label='Close Price', color='blue')
    ax1.plot(hist.index, hist['MA20'], label='20-day MA', color='orange', alpha=0.7)
    ax1.plot(hist.index, hist['MA50'], label='50-day MA', color='red', alpha=0.7)
    ax1.fill_between(hist.index, hist['BB_upper'], hist['BB_lower'], alpha=0.1, color='gray', label='Bollinger Bands')
    ax1.set_title(f"{ticker} Technical Analysis")
    ax1.set_ylabel("Price ($)")
    ax1.legend()
    ax1.grid(True)
    ax2.plot(hist.index, hist['RSI'], color='purple', label='RSI')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
    ax2.set_ylabel("RSI")
    ax2.legend()
    ax2.grid(True)
    ax3.plot(hist.index, hist['MACD'], label='MACD', color='blue')
    ax3.plot(hist.index, hist['Signal_Line'], label='Signal Line', color='orange')
    ax3.bar(hist.index, hist['MACD'] - hist['Signal_Line'], color=['green' if x > 0 else 'red' for x in (hist['MACD'] - hist['Signal_Line'])], alpha=0.3)
    ax3.set_ylabel("MACD")
    ax3.legend()
    ax3.grid(True)
    plt.tight_layout()
    return fig

# AI prompt and chain setup
def get_chain():
    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )
    prompt = PromptTemplate(
        input_variables=["ticker", "data", "technical_data"],
        template="""
You are a financial analyst. Here is historical data for the stock {ticker}:

Price Data:
{data}

Technical Indicators:
{technical_data}

Provide an analysis in the following format:

Executive Summary:
[2-3 sentence overview]

Technical Analysis:
1. Moving Averages: [Analyze MA20 and MA50 trends and crossovers]
2. RSI Analysis: [Interpret RSI values and potential signals]
3. MACD: [Analyze MACD and Signal Line crossovers]
4. Bollinger Bands: [Comment on price position relative to bands]

Key Observations:
1. [Price trend observation]
2. [Technical signal observation]
3. [Volume analysis]
4. [Risk/volatility assessment]

Recommendations for Investors:
- Short-term outlook (1-2 weeks)
- Medium-term outlook (1-3 months)
- Long-term outlook (1 year +)
"""
    )
    return LLMChain(llm=llm, prompt=prompt) 