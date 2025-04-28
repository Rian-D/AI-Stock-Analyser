import streamlit as st
import yfinance as yf
import os
from analysis import calculate_technical_indicators, plot_technical_analysis, get_chain
from news import fetch_news, render_news_card
from dotenv import load_dotenv
from io import BytesIO, StringIO

# Load environment variables from .env file
load_dotenv()

# --- STREAMLIT UI ---
st.set_page_config(page_title="📈 Stock Analyser", layout="wide")
st.title("📈 Stock Analyser")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)", "AAPL")

if st.button("Analyse"):
    with st.spinner("Fetching stock data, news, and generating analysis..."):
        try:
            # --- STOCK DATA ---
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo")
            
            # Calculate technical indicators
            hist = calculate_technical_indicators(hist)
            
            # Prepare data for analysis
            data = hist[['Close', 'Volume']].tail(10).to_string()
            technical_data = hist[['MA20', 'MA50', 'RSI', 'MACD', 'ATR']].tail(5).to_string()

            # --- KEY METRICS ---
            st.markdown("### Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"${hist['Close'][-1]:.2f}")
            with col2:
                st.metric("RSI", f"{hist['RSI'][-1]:.2f}")
            with col3:
                st.metric("MACD", f"{hist['MACD'][-1]:.2f}")
            with col4:
                st.metric("ATR", f"{hist['ATR'][-1]:.2f}")

            # --- RAW DATA (in expander) ---
            with st.expander("Show Raw Data Tables"):
                st.subheader("Recent Price & Volume Data")
                st.dataframe(hist[['Close', 'Volume']].tail(10))
                st.subheader("Recent Technical Indicators")
                st.dataframe(hist[['MA20', 'MA50', 'RSI', 'MACD', 'ATR']].tail(5))
                # --- Download Data as CSV ---
                csv_bytes = hist.to_csv().encode('utf-8')
                st.download_button(
                    label="Download Data as CSV",
                    data=csv_bytes,
                    file_name=f"{ticker}_historical_data.csv",
                    mime="text/csv"
                )

            # --- TABS FOR MAIN SECTIONS ---
            tabs = st.tabs(["🤖 AI Analysis", "📊 Technical Charts", "📰 News & Sentiment"])

            # --- AI ANALYSIS TAB ---
            with tabs[0]:
                chain = get_chain()
                result = chain.run(ticker=ticker, data=data, technical_data=technical_data)
                st.markdown("## 🤖 AI Analysis")
                for section in result.split('\n\n'):
                    if section.strip():
                        if any(section.strip().startswith(prefix) for prefix in ['1.', '-', '* '] ):
                            st.markdown(section)
                        else:
                            st.markdown(f"<div style='margin-bottom: 1rem;'>{section}</div>", unsafe_allow_html=True)

            # --- TECHNICAL CHARTS TAB ---
            with tabs[1]:
                st.markdown("## 📊 Technical Analysis")
                fig = plot_technical_analysis(hist, ticker)
                st.pyplot(fig)
                # --- Download Chart as PDF ---
                pdf_bytes = BytesIO()
                fig.savefig(pdf_bytes, format='pdf')
                pdf_bytes.seek(0)
                st.download_button(
                    label="Download Chart as PDF",
                    data=pdf_bytes,
                    file_name=f"{ticker}_technical_analysis.pdf",
                    mime="application/pdf"
                )

            # --- NEWS & SENTIMENT TAB ---
            with tabs[2]:
                st.markdown("## 📰 Recent News and Sentiment")
                company_name = stock.info.get('longName', ticker)
                news_api_key = os.environ.get('NEWS_API_KEY')
                articles = fetch_news(ticker, company_name, news_api_key)
                displayed_count = 0
                for article in articles:
                    news_card = render_news_card(article, company_name, ticker)
                    if news_card:
                        st.markdown(news_card, unsafe_allow_html=True)
                        displayed_count += 1
                    if displayed_count >= 5:
                        break
                if displayed_count == 0:
                    st.info(f"No relevant news found in the last 30 days for {company_name} ({ticker}). Try adjusting the search parameters.")
        except Exception as e:
            st.error(f"Error: {e}")
