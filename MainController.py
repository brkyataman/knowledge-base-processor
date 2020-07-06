from flask import Flask, jsonify, request
from flask import render_template
import os
import requests
import json
import pymysql
from WordEmbeddingManager import WordEmbeddingManager
from SparqlManager import SparqlManager
from FastTextBuilder import FastTextBuilder

app = Flask(__name__)
wordEmbeddingManager = WordEmbeddingManager()
fastTextBuilder = FastTextBuilder()
sparqlManager = SparqlManager("neuroboun_fasttext")


@app.route('/')
def greetings():
    return render_template('query_page.html')


@app.route('/similars/<input>')
def get_similars(input):
    #similars = wordEmbeddingManager.get_similar_terms(word=input, topn=5)
    similars = fastTextBuilder.get_similar_terms(word=input,topn=5)
    return jsonify(similars)


@app.route('/query', methods=["POST"])
def query():
    data = request.json

    details, articles = sparqlManager.get_related_articles_of_list(data["list"], data["min_sim_score"])

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