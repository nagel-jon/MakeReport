import os
import sys
from datetime import datetime, timedelta, date
from urllib.parse import urlparse
from bson import ObjectId

import pandas as pd
import requests
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__)

# MongoDB Config
def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    news_articles = db.news_articles
    topics = db.topics
    sources = db.sources
    reports = db.reports
    batches = db.batches
    
    return client, db, news_articles, topics, sources, reports, batches

# Helper functions
def perform_search_article_mongo(query):
    # Use the query to search the MongoDB collection and retrieve the results
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
    result_cursor = news_articles.find({"title": {"$regex": f'.*{query}.*', "$options": "i"}})
    results_df = pd.DataFrame(list(result_cursor))

    # Convert DataFrame to HTML with custom styles
    html_table = results_df.to_html(classes='table table-bordered', index=False)
    return html_table

def search_source_mongo(query):
    # Perform a case-insensitive search in MongoDB collection
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
    result_cursor = sources.find({'name': {'$regex': f'.*{query}.*', '$options': 'i'}})
    results_df = pd.DataFrame(list(result_cursor))

    # Convert DataFrame to HTML with custom styles
    html_table = results_df.to_html(classes='table table-bordered', index=False)
    return html_table

def perform_search_report_mongo(query):
    # Use the query to search the MongoDB collection and retrieve the results
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
    result_cursor = reports.find({"report": {"$regex": f'.*{query}.*', "$options": "i"}})
    results_df = pd.DataFrame(list(result_cursor))

    # Convert DataFrame to HTML with custom styles
    html_table = results_df.to_html(classes='table table-bordered', index=False)
    return html_table

def get_sources_from_url(article, batch_name):
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()

    url = article.get("url", "")
    article_id = article.get("_id", "")
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    source = {
        "name": domain,
        "url": url,
        "article_id": article_id,
        "batch_name": batch_name
    }
    db.sources.insert_one(source)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/view_reports', methods=['GET', 'POST'])
def view_reports():
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
    collection = db.reports
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_df = perform_search_report_mongo(search_query)

        html_table = results_df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('search_reports.html', tables=[html_table], titles=results_df.columns.values, search_query=search_query)
    else:
        # Handle the regular display of articles without a search query
        reports_df = pd.DataFrame(list(reports.find()))
        report_html = reports_df.to_html(classes='table table-striped table-bordered', index=False)
        
        # Render the template with the default reports table
        return render_template('view_reports.html', report_table=report_html, articles_table=None)


@app.route('/view_articles', methods=['GET', 'POST'])
def view_articles():
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
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
    client, db, news_azticles, topics, sources, reports, batches = connect_to_mongodb()
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

@app.route('/view_batches', methods=['GET', 'POST'])
def view_batches():
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
    collection = db.batches
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_df = search_source_mongo(search_query)

        html_table = results_df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('search_result.html', tables=[html_table], titles=results_df.columns.values, search_query=search_query)
    else:
        # Handle the regular display of articles without a search query
        df = pd.DataFrame(list(collection.find()))
        html_table = df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('view_batches.html', tables=[html_table], titles=df.columns.values)



@app.route('/generate_report', methods=['GET'])
def generate_report():
    return render_template('generate_report.html')

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

@app.route('/get_articles', methods=['GET', 'POST'])
def get_articles_by_keyword():
    if request.method == 'POST':
        search_query = request.form['keyword']
        client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
        batch_name = "batch" + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
        news_articles = db.news_articles

        # Call News API here with search_query
        # Need current date for API call
        current_date = date.today()
        three_days_ago = current_date - timedelta(days=3)

        # Calling newsAPI to get new stories
        url = ('https://newsapi.org/v2/everything?'
            f'q={search_query}&'
            f'from={three_days_ago}&'
            'sortBy=popularity&'
            f'apiKey={os.getenv("NEWS_API_KEY")}')

        response = requests.get(url)

        # Check if the API request was successful
        if response.status_code == 200:
            # Extract and clean the articles
            articles = response.json().get("articles", [])



            # Insert cleaned articles into the database
            for article in articles:
                cleaned_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "urlToImage": article.get("urlToImage", ""),
                    "publishedAt": article.get("publishedAt", ""),
                    "content": article.get("content", ""),
                    "batch_name": batch_name
                }
                news_articles.insert_one(cleaned_article)
                get_sources_from_url(cleaned_article, batch_name)
                

            batches.insert_one({"batch_name": batch_name})

            df = pd.DataFrame(list(news_articles.find({"batch_name": batch_name})))
            html_table = df.to_html(classes='table table-striped table-bordered', index=False)
            return render_template('view_articles.html', tables=[html_table], titles=df.columns.values, search_query=search_query)
    else:
        return render_template('get_articles.html')

@app.route('/generate_report_from_articles', methods=['GET', 'POST'])
def generate_report_from_articles():
    if request.method == 'POST':
        # Handle the POST request to generate the report
        client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
        search_query = request.form['search_query']
        batch_name = request.form['batch_name']

        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Get the article content from MongoDB
        articles = news_articles.find({"batch_name": batch_name})
        print (articles)
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
            "batch_name": batch_name
        }

        reports.insert_one(report_data)

        return render_template('generate_report_from_articles.html', search_query=search_query, report=report_data)
    
    else:
        client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()

        df = pd.DataFrame(list(batches.find()))
        html_table = df.to_html(classes='table table-striped table-bordered', index=False)
        return render_template('/generate_report_from_articles.html', tables=[html_table], titles=df.columns.values )

    
@app.route('/query_report', methods=['GET', 'POST'])
def query_report():
    client, db, news_articles, topics, sources, reports, batches = connect_to_mongodb()
    if request.method == 'POST':
        # If a search is entered, fetch the report and associated articles
        report_id = request.form['search_query']

        try:
            # Convert the string report_id to ObjectId
            report_id_obj = ObjectId(report_id)
            report = reports.find_one({"_id": report_id_obj})

            if report:
                # Convert the report dictionary to a DataFrame
                report_df = pd.DataFrame([report])

                # Get the list of article IDs used to generate the report
                article_ids = report.get("article_ids", [])
                print(article_ids)
                
                # Fetch the articles from MongoDB using the list of article IDs
                articles = news_articles.find({"_id": {"$in": article_ids}})
                articles_df = pd.DataFrame(list(articles))
                
                # Convert DataFrames to HTML tables
                report_html = report_df.to_html(classes='table table-striped table-bordered', index=False)
                articles_html = articles_df.to_html(classes='table table-striped table-bordered', index=False)
                
                # Render the template with report and articles tables
                return render_template('view_reports.html', report_table=report_html, articles_table=articles_html)
        except Exception as e:
            print(f"Error: {e}")

    else:
        # If no search is entered, display the default table of reports
        reports_df = pd.DataFrame(list(reports.find()))
        report_html = reports_df.to_html(classes='table table-striped table-bordered', index=False)
        
        # Render the template with the default reports table
        return render_template('view_reports.html', report_table=report_html, articles_table=None)



    
if __name__ == '__main__':
    app.run(debug=True)