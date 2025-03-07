from flask import Flask, request, jsonify
from flask_cors import CORS

from search import search
dir = './index'

app = Flask(__name__)
CORS(app)

@app.get('/search')
def search_path():
    query = request.args.get('q')
    if not query:
        return "error: no query provided", 400
    print(type(query))

    urls = search(query, dir)

    return jsonify([url[0] for url in urls])