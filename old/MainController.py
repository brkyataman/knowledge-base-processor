from flask import Flask, jsonify, request
from flask import render_template
import os
import requests
import json
import pymysql
from WordEmbeddingManager import WordEmbeddingManager
from SparqlManager import SparqlManager

app = Flask(__name__)
wordEmbeddingManager = WordEmbeddingManager()
sparqlManager = SparqlManager()


@app.route('/')
def greetings():
    return render_template('query_page.html')


@app.route('/similars/<input>')
def get_similars(input):
    similars = wordEmbeddingManager.get_similars(query=input, topn=5)
    return jsonify(similars)

@app.route('/query', methods=["POST"])
def query():
    data = request.json

    details, articles = sparqlManager.get_related_articles_of_list(data["list"])

    result = {"details": details, "articles": articles}

    return jsonify(result)



def GetDbConnection():
    return pymysql.connect(host='localhost',
        user='root',
        password='pass',
        db='testdb',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

app.run(debug=True)