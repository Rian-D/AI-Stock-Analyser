import os
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# HTML template for news cards
NEWS_CARD_TEMPLATE = """
<div style='padding: 15px; border-left: 5px solid {border_color}; margin-bottom: 15px; background-color: rgba(255,255,255,0.05); border-radius: 5px;'>
    <h4><a href="{url}" target="_blank" style="color: inherit; text-decoration: none; hover: underline;">{title}</a></h4>
    <p><i>{description}</i></p>
    <p><b>Source:</b> {source} | <b>Date:</b> {published} | <b>Sentiment:</b> {sentiment_label}</p>
</div>
"""

def fetch_news(ticker, company_name, api_key, days=30, page_size=15):
    """Fetch relevant news articles for a given ticker and company name."""
    newsapi = NewsApiClient(api_key=api_key)
    from datetime import datetime, timedelta
    domains = ','.join([
        'reuters.com',
        'bloomberg.com',
        'cnbc.com',
        'finance.yahoo.com',
        'marketwatch.com',
        'fool.com',
        'investors.com',
        'seekingalpha.com',
        'barrons.com',
        'wsj.com',
        'ft.com',
        'forbes.com',
        'businessinsider.com',
        'markets.businessinsider.com',
        'thestreet.com',
        'zacks.com',
        'morningstar.com',
        'nasdaq.com',
        'benzinga.com',
        'investing.com'
    ])
    articles = newsapi.get_everything(
        q=f'({ticker} OR "{company_name}")',
        language='en',
        sort_by='publishedAt',
        page_size=page_size,
        from_param=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
        domains=domains
    )
    return articles['articles'] if 'articles' in articles else []

def analyze_sentiment(title, description):
    """Headline-weighted VADER sentiment analysis with positive/negative phrase override."""
    text = f"{title}. {description}"
    scores = analyzer.polarity_scores(text)
    headline_scores = analyzer.polarity_scores(title)
    compound = 0.7 * headline_scores['compound'] + 0.3 * scores['compound']

    negative_phrases = [
        "no longer", "lost", "decline", "fall", "drop", "bear", "mess", "worse", "not", 
        "struggle", "risk", "concern", "sell", "damage", "losing", "slowing", 
        "loss", "slow", "problem", "crash", "worry", "worried"
    ]
    positive_phrases = [
        "record high", "outperform", "growth", "beat", "surge", "rally", "bull", 
        "strong", "gain", "profit", "improve", "upgrade", "buy", "rebound", 
        "positive", "exceed", "buy", "gain", "gaining", "profit", "winning", "expanding", "expand", "expansion"
    ]

    # Combine title and description for phrase checking
    full_text = (title + " " + (description or "")).lower()
    # Phrase-based overrides
    pos = any(phrase in full_text for phrase in positive_phrases)
    neg = any(phrase in full_text for phrase in negative_phrases)
    if pos and not neg:
        return "🟢 Positive", "#66cc00"
    if neg and not pos:
        return "🔴 Negative", "#cc3300"

    # VADER score-based sentiment if no phrase matches or if both positive and negative phrase matches
    if compound > 0.1:
        return "🟢 Positive", "#66cc00"
    elif compound < -0.1:
        return "🔴 Negative", "#cc3300"
    else:
        return "🟡 Neutral", "#cccc00"

def render_news_card(article, company_name, ticker):
    """Render a news article as an HTML card."""
    title = article['title']
    description = article.get('description', '')
    published = article.get('publishedAt', '').split('T')[0]
    source = article.get('source', {}).get('name', '')
    url = article.get('url', '')
    
    # Relevance check
    title_desc = (title + " " + description[:100]).lower()
    is_relevant = (
        ticker.lower() in title_desc or 
        any(word.lower() in title_desc for word in company_name.split())
    )
    if not is_relevant:
        return None
        
    sentiment_label, border_color = analyze_sentiment(title, description)
    return NEWS_CARD_TEMPLATE.format(
        title=title,
        url=url,
        description=description,
        source=source,
        published=published,
        sentiment_label=sentiment_label,
        border_color=border_color
    ) 