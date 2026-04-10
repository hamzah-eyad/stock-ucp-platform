import requests
import os
from textblob import TextBlob
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(query, max_articles=10):
    # Fetch news articles related to the given query from NewsAPI
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Return empty list if no articles found
    if data.get("status") != "ok":
        return []

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "url": article.get("url", ""),
            "publishedAt": article.get("publishedAt", "")
        })
    return articles

def analyze_sentiment(text):
    # Analyze the sentiment of a given text using TextBlob
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity

    # Classify sentiment based on polarity score
    if score > 0.1:
        return "Positive", score
    elif score < -0.1:
        return "Negative", score
    else:
        return "Neutral", score

def get_risk_indicator(articles):
    # Calculate overall geopolitical risk based on article sentiments
    if not articles:
        return "Unknown", 0

    total_score = 0
    for article in articles:
        text = article["title"] + " " + (article["description"] or "")
        _, score = analyze_sentiment(text)
        total_score += score

    avg_score = total_score / len(articles)

    # Return risk level based on average sentiment score
    if avg_score > 0.1:
        return "Low Risk 🟢", avg_score
    elif avg_score < -0.1:
        return "High Risk 🔴", avg_score
    else:
        return "Medium Risk 🟡", avg_score

def get_news_with_sentiment(query):
    # Fetch news and attach sentiment analysis to each article
    articles = get_news(query)
    results = []
    for article in articles:
        text = article["title"] + " " + (article["description"] or "")
        sentiment, score = analyze_sentiment(text)
        results.append({
            "title": article["title"],
            "url": article["url"],
            "publishedAt": article["publishedAt"],
            "sentiment": sentiment,
            "score": round(score, 3)
        })
    return results