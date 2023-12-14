# MakeReport
Database Systems 4620 Final Project
Jonathan Nagel jn855420@ohio.edu

Instructions:
1. Clone Repo to Local Machine
2. Install MongoDB Community Edition Locally
3. Navigate to Repository Directory
4. Activate Python Virtual Environment (source venv/bin/activate for linux)
5. Install Python Packages (list below)
6. Add API Keys to Environment or .env file
7. Run app with flask run
8. Go to http://localhost:5000/ in browser to view

Goal: To Make News Reports synthesizing Online News Media  
MakeReport works by gathering News Sources Based on either Keyword Search. Allowing for report generation for a specific topic of interest or a point in time.


The user is then prompted to enter their instructions for report generation.

This can all be done in natural language as the report generation is done by ChatGPT 3.5 Turbo. When a user creates a report, it is put into a database collection along with information about the news articles used to write it. The user can then search through reports, articles, and sources via text.



3 Query Types:
1. String Matching
2. Report and Batch Query
3. Boolean Date Comparison

Python Libraries Used:
pip install pandas
pip install Flask
pip install pymongo
pip install dotenv
pip install openai
