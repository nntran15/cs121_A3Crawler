from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from google import genai
from google.genai import types

import os
import requests

from search import search
dir = './index'

# Setup flask
app = Flask(__name__)
CORS(app)

# load env vars
load_dotenv()

# setup gemini api
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
sys_instruct = "You are a website summarizer for a search engine. Your goal is to summarize scraped clean text for users to look at. Summarize the following content"

# Search functionality
@app.get('/search')
def search_path():
    query = request.args.get('q')
    if not query:
        return "error: no query provided", 400

    urls = search(query, dir)

    return jsonify([url[0] for url in urls])

# LLM summary
@app.get("/summary")
def summarize():
    url = request.args.get('q')
    if not url:
        return "error: no query provided", 400
    
    # scraping time
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    clean_text = soup.get_text()
    clean_text = clean_text[:150000] + (clean_text[150000:] and '... truncated because text exceeded 150,000 characters')
    # gemini time
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=[f'URL: {url}, content: {clean_text}'],
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct
        )
    )
        
    return response.text