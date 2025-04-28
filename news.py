import os
from newsapi import NewsApiClient
from textblob import TextBlob

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
    """Analyze sentiment of a news article's title and description."""
    text = f"{title}. {description}"
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "🟢 Positive", "#66cc00"
    elif polarity < 0:
        return "🔴 Negative", "#cc3300"
    else:
        return "🟡 Neutral", "#cccc00"

def render_news_card(article, company_name, ticker, template_path=None):
    """Render a news article as an HTML card using the provided template."""
    if template_path is None:
        template_path = os.path.join(os.path.dirname(__file__), 'news_card_template.html')
    with open(template_path, 'r') as f:
        news_card_template = f.read()
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
    return news_card_template.format(
        title=title,
        url=url,
        description=description,
        source=source,
        published=published,
        sentiment_label=sentiment_label,
        border_color=border_color
    ) 