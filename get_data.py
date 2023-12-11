import os
import sys
import requests
from datetime import datetime, timedelta, date
from pymongo import MongoClient

# MongoDB Config

client = MongoClient('mongodb://localhost:27017/')
db = client.MakeReport
news_articles = db.news_articles
topics = db.topics
sources = db.sources

#Sample Data Search Keyword
search_query = "Crypto"

#Getting Sample Articles Data

current_date = date.today()
three_days_ago = current_date - timedelta(days=3)

# Calling newsAPI to get new stories
url = ('https://newsapi.org/v2/everything?'
f'q={search_query}&'
f'from={three_days_ago}&'
'sortBy=popularity&'
'apiKey={os.environ.get("NEWS_API_KEY")}}')

response = requests.get(url)

# Check if the API request was successful
if response.status_code == 200:
    # Extract and clean the articles
    articles = response.json().get("articles", [])

    # Insert cleaned articles into the database
    # for article in articles:
    #     cleaned_article = {
    #         "title": article.get("title", ""),
    #         "description": article.get("description", ""),
    #         "url": article.get("url", ""),
    #         "urlToImage": article.get("urlToImage", ""),
    #         "publishedAt": article.get("publishedAt", ""),
    #         "content": article.get("content", "")
    #     }

    #     news_articles.insert_one(cleaned_article)

    #Getting Sample Sources Data
    sample_sources = [
        {"name": "CNN"},
        {"name": "BBC"},
        {"name": "Reuters"},
        {"name": "The New York Times"},
        {"name": "The Guardian"}
    ]

    sources.insert_many(sample_sources)

    

    
