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
    # client = MongoClient('mongodb://localhost:27017/')
    # db = client.local
    # collection = db.startup_log
    
    # df = pd.DataFrame(list(collection.find()))

    # return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
    return render_template('index.html')

    

@app.route('/view_collections', methods=['GET'])
def view_collections():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.local
    collection = db.startup_log
    
    df = pd.DataFrame(list(collection.find()))

    return render_template('view_collections.html', tables=[df.to_html(classes='data')], titles=df.columns.values)



@app.route('/view_articles', methods=['GET', 'POST'])
def view_articles():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.news_articles
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_df = search_article_mongo(search_query)

        html_table = results_df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('search_result.html', tables=[html_table], titles=results_df.columns.values, search_query=search_query)
    else:
        # Handle the regular display of articles without a search query
        df = pd.DataFrame(list(collection.find()))
        html_table = df.to_html(classes='table table-striped table-bordered', index=False)

        return render_template('view_articles.html', tables=[html_table], titles=df.columns.values, search_query=None)

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

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        results_table = search_article_mongo(search_query)

        return render_template('search_result.html', query=search_query, results_table=results_table)
    else:
        return render_template('search.html')



def search_article_mongo(query):
    # Perform a case-insensitive search in MongoDB collection
    result_cursor = news_articles.find({'title': {'$regex': f'.*{query}.*', '$options': 'i'}})
    results_df = pd.DataFrame(list(result_cursor))

    # Apply custom styles to the HTML table
    custom_styles = """
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }

            th, td {
                text-align: left;
                padding: 8px;
            }

            tr:nth-child(even) {
                background-color: #f2f2f29d;
            }

            th {
                background-color: #375e94;
                color: white;
            }
        </style>
    """

    # Convert DataFrame to HTML with custom styles
    html_table = custom_styles + results_df.to_html(classes='table table-bordered', index=False)
    return html_table



def search_source_mongo(query):
    # Perform a case-insensitive search in MongoDB collection
    result_cursor = sources.find({'name': {'$regex': f'.*{query}.*', '$options': 'i'}})
    results_df = pd.DataFrame(list(result_cursor))

    # Apply custom styles to the HTML table
    custom_styles = """
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }

            th, td {
                text-align: left;
                padding: 8px;
            }

            tr:nth-child(even) {
                background-color: #f2f2f29d;
            }

            th {
                background-color: #375e94;
                color: white;
            }
        </style>
    """

    # Convert DataFrame to HTML with custom styles
    html_table = custom_styles + results_df.to_html(classes='table table-bordered', index=False)
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





    

    

