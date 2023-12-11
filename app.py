import os
import sys
from openai import OpenAI
import requests
from datetime import datetime, timedelta, date
from pymongo import MongoClient
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import pandas as pd
from dotenv import load_dotenv

app = Flask(__name__)

# MongoDB Config
client = MongoClient('mongodb://localhost:27017/')
db = client.MakeReport
news_articles = db.news_articles
topics = db.topics
sources = db.sources

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')



@app.route('/view_articles', methods=['GET', 'POST'])
def view_articles():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.news_articles
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_df = perform_search_article_mongo(search_query)

        html_table = results_df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('search_articles.html', tables=[html_table], titles=results_df.columns.values, search_query=search_query)
    else:
        # Handle the regular display of articles without a search query
        df = pd.DataFrame(list(collection.find()))
        search_query = None
        html_table = df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('view_articles.html', tables=[html_table], titles=df.columns.values, search_query=search_query)

@app.route('/view_sources', methods=['GET', 'POST'])
def view_sources():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.sources
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_df = search_source_mongo(search_query)


        html_table = results_df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('search_result.html', tables=[html_table], titles=results_df.columns.values, search_query=search_query)
    else:
        # Handle the regular display of articles without a search query
        df = pd.DataFrame(list(collection.find()))
        html_table = df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('view_sources.html', tables=[html_table], titles=df.columns.values)



@app.route('/generate_report', methods=['GET'])
def generate_report():
    return render_template('generate_report.html')

def search_articles():
    query = request.args.get('query')
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.news_articles

    df = pd.DataFrame(list(collection.find({'$text': {'$search': query}})))
    return render_template('view_articles.html', tables=[df.to_html(classes='data')], titles=df.columns.values)



@app.route('/search_articles', methods=['GET', 'POST'])
def search_articles():
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_table = perform_search_article_mongo(search_query)

        return render_template('search_result.html', query=search_query, results_table=results_table)
    else:
        return render_template('search_article.html')


@app.route('/search_sources', methods=['GET', 'POST'])
def search_sources():
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_table = search_source_mongo(search_query)

        return render_template('search_result.html', query=search_query, results_table=results_table)
    else:
        return render_template('search_source.html')


def perform_search_article_mongo(query):
    # Use the query to search the MongoDB collection and retrieve the results
    result_cursor = news_articles.find({"title": {"$regex": f'.*{query}.*', "$options": "i"}})
    results_df = pd.DataFrame(list(result_cursor))

    # Convert DataFrame to HTML with custom styles
    html_table = results_df.to_html(classes='table table-bordered', index=False)
    return html_table




def search_source_mongo(query):
    # Perform a case-insensitive search in MongoDB collection
    result_cursor = sources.find({'name': {'$regex': f'.*{query}.*', '$options': 'i'}})
    results_df = pd.DataFrame(list(result_cursor))


    # Convert DataFrame to HTML with custom styles
    html_table = results_df.to_html(classes='table table-bordered', index=False)
    return html_table

@app.route('/generate_report_by_keyword', methods=['GET', 'POST'])
def generate_report_by_keyword():
    if request.method == 'POST':
        keyword = request.form['keyword']
        report_df = get_report_data(keyword)

        # Convert DataFrame to HTML table
        report_table = report_df.to_html(classes='table table-bordered', index=False)

        return render_template('generate_report_by_keyword.html', report_table=report_table)
    else:
        return render_template('generate_report_by_keyword.html')

@app.route('/get_articles', methods=['GET', 'POST'])
def get_articles_by_keyword():
    if request.method == 'POST':
        search_query = request.form['keyword']
        client = MongoClient('mongodb://localhost:27017/')
        db = client.MakeReport
        news_articles = db.news_articles

        #Call News API here with search_query
        # Need current date for API call
        current_date = date.today()
        three_days_ago = current_date - timedelta(days=3)

        # Calling newsAPI to get new stories
        url = ('https://newsapi.org/v2/everything?'
            f'q={search_query}&'
            f'from={three_days_ago}&'
            'sortBy=popularity&'
            'apiKey=f84359a7c186476588c807200d3b467f')

        response = requests.get(url)

        # Check if the API request was successful
        if response.status_code == 200:
            # Extract and clean the articles
            articles = response.json().get("articles", [])

            # Clear previous data in the database
            news_articles.delete_many({})

            # Insert cleaned articles into the database
            for article in articles:
                cleaned_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "content": article.get("content", "")
                }
                news_articles.insert_one(cleaned_article)

            df = pd.DataFrame(list(news_articles.find()))
            html_table = df.to_html(classes='table table-striped table-bordered', index=False)
            return render_template('view_articles.html', tables=[html_table], titles=df.columns.values, search_query=search_query)
    else:
        return render_template('get_articles.html')

# Sample function to simulate API call based on keyword
def get_report_data(keyword):
    # This is where you would make your API call using the provided keyword
    # Replace the following lines with your actual API call and data processing
    data = {
        'Title': ['Result 1', 'Result 2', 'Result 3'],
        'Description': ['Description 1', 'Description 2', 'Description 3']
    }
    return pd.DataFrame(data)


if __name__ == '__main__':
    app.run(debug=True)





    

    

