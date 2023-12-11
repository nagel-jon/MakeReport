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
    # db = client.MakeReport
    # news_articles = db.news_articles
    # topics = db.topics
    # sources = db.sources

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.local
    collection = db.startup_log
    
    df = pd.DataFrame(list(collection.find()))

    return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

    

    

@app.route('/view_collections', methods=['GET'])
def view_collections():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.local
    collection = db.startup_log
    
    df = pd.DataFrame(list(collection.find()))

    return render_template('view_collections.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/view_articles', methods=['GET'])
def view_articles():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.news_articles
    
    df = pd.DataFrame(list(collection.find()))

    return render_template('view_articles.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/view_sources', methods=['GET'])
def view_sources():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.MakeReport
    collection = db.sources
    
    df = pd.DataFrame(list(collection.find()))

    return render_template('view_sources.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/generate_report', methods=['GET'])
def generate_report():


    return render_template('generate_report.html')

if __name__ == '__main__':
    app.run(debug=True)



