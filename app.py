import os
import sys
from openai import OpenAI
import requests
from datetime import datetime, timedelta, date
from pymongo import MongoClient
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import urlparse

app = Flask(__name__)

# MongoDB Config
client = MongoClient('mongodb://localhost:27017/')
db = client.MakeReport
news_articles = db.news_articles
topics = db.topics
sources = db.sources
reports = db.reports

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/view_reports', methods=['GET', 'POST'])
def view_reports():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.reports
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_df = perform_search_report_mongo(search_query)

        html_table = results_df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('search_reports.html', tables=[html_table], titles=results_df.columns.values, search_query=search_query)
    else:
        # Handle the regular display of articles without a search query
        df = pd.DataFrame(list(collection.find()))
        search_query = None
        html_table = df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('view_reports.html', tables=[html_table], titles=df.columns.values, search_query=search_query)


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

def perform_search_report_mongo(query):
    # Use the query to search the MongoDB collection and retrieve the results
    result_cursor = reports.find({"report": {"$regex": f'.*{query}.*', "$options": "i"}})
    results_df = pd.DataFrame(list(result_cursor))

    # Convert DataFrame to HTML with custom styles
    html_table = results_df.to_html(classes='table table-bordered', index=False)
    return html_table

# @app.route('/generate_report_by_keyword', methods=['GET', 'POST'])
# def generate_report_by_keyword():
#     if request.method == 'POST':
#         keyword = request.form['keyword']
#         report_df = get_report_data(keyword)

#         # Convert DataFrame to HTML table
#         report_table = report_df.to_html(classes='table table-bordered', index=False)

#         return render_template('generate_report_by_keyword.html', report_table=report_table)
#     else:
#         return render_template('generate_report_by_keyword.html')



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
            'apiKey=[os.getenv("NEWS_API_KEY")]')

        response = requests.get(url)

        # Check if the API request was successful
        if response.status_code == 200:
            # Extract and clean the articles
            articles = response.json().get("articles", [])

            # Clear previous data in the database
            news_articles.delete_many({})

            #Clear Sources List 
            sources.delete_many({})

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
                get_sources_from_url(cleaned_article)
                


            df = pd.DataFrame(list(news_articles.find()))
            html_table = df.to_html(classes='table table-striped table-bordered', index=False)
            return render_template('view_articles.html', tables=[html_table], titles=df.columns.values, search_query=search_query)
    else:
        return render_template('get_articles.html')



def get_sources_from_url(article):
    url = article.get("url", "")
    article_id = article.get("_id", "")
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    source = {
        "name": domain,
        "url": url,
        "article_id": article_id
    }
    db.sources.insert_one(source)


@app.route('/generate_report_from_articles', methods=['GET', 'POST'])
def generate_report_from_articles():
    if request.method == 'POST':
        # Handle the POST request to generate the report
        search_query = request.form['search_query']

        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Get the article content from MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client.MakeReport
        news_articles = db.news_articles

        articles = news_articles.find()

        # Concatenate article titles and content with search_query
        report = search_query
        character_count = len(report)
        used_article_ids = []  # Initialize an empty list to store the article IDs

        for article in articles:
            article_id = article.get('_id', '')  # Get the article ID
            used_article_ids.append(article_id)  # Add the article ID to the list

            title = article.get('title', '')
            content = article.get('content', '')

            report += title[:30] + content[:100]
            character_count = len(report)

            if character_count >= 4500:
                break
        print(report)

        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are synthesizing news stories into a tweet."},
                {"role": "user", "content": report},
            ]
        )
        gpt_response_content = completion.choices[0].message.content

        reports = db.reports

        report_data = {
            "search_query": search_query,
            "report": gpt_response_content,
            "article_ids": used_article_ids,
        }

        reports.insert_one(report_data)

        return render_template('generate_report_from_articles.html', search_query=search_query, report=report_data)
    
    else:
        # Handle the GET request, define an empty report
        report_data = {"search_query": "", "report": "", "article_ids": []}
        return render_template('generate_report_from_articles.html', search_query="", report=report_data)



if __name__ == '__main__':
    app.run(debug=True)



    
    


    

    

