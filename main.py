import json
from flask import Flask, render_template, request
from whoosh.index import open_dir   
from whoosh import scoring
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from search_vector import search as srch
import glob

import subprocess

from werkzeug.utils import secure_filename
from docx import Document
import os


app = Flask(__name__)

@app.route('/clear')
def clear():
    dirs = ["tmp", "documents", "indexdir"]
    for dir in dirs:
        files = glob.glob(os.path.join(dir, '*'))
        if files:
            for file in files:
                os.remove(file)
    return render_template("home.html")

@app.route("/")
def homePage():
    return render_template("home.html")

@app.route("/searchpage")
def searchPage():
    return render_template("search.html")

@app.route("/upload")
def uploadPage():
    return render_template("upload.html")

algorithm = ""

def set_algorithm(value):
    global algorithm
    algorithm = value

@app.route("/index" ,methods=['POST'])
def index():

    algorithm = request.form.get("algorithm")
    set_algorithm(algorithm)
    if 'documents' not in request.files:
        return 'No file part'
    files = request.files.getlist('documents')
    for file in files:
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file.save(os.path.join('documents', filename))

    subprocess.call(['python', 'indexing.py'])
    subprocess.call(['python', 'indexing_vector.py'])
    return render_template("home.html")

@app.route("/search")
def search():
    global algorithm
    ix = open_dir("indexdir")
    
    query = request.args.get("query")
    model = request.args.get("model")
    threshold = request.args.get("threshold")
    threshold = float(threshold)
    isVector = False
    weighting = scoring.BM25F
    if model == "boolean":
        parser = QueryParser("content", schema=ix.schema)
        if algorithm == "TF_IDF":
            weighting = scoring.TF_IDF()
        elif algorithm == "BM25F":
            weighting = scoring.BM25F

    elif model == "boolean_extended":
        parser = QueryParser("content", schema=ix.schema, group=OrGroup)
        if algorithm == "TF_IDF":
            weighting = scoring.TF_IDF()
        elif algorithm == "BM25F":
            weighting = scoring.BM25F

    elif model == "vector":
        isVector = True
    else:
        raise ValueError("Invalid model selected")

    if isVector:
        results = srch(query,threshold=threshold)
        results_list = []
        
        
        

        for r in results:
            resultRank = results[r]['rank']
            resultsSntns = results[r]['sentences']
            resultsTitle = r
            rank = ""
            for i in range(int(round(resultRank*100,0)/5)):
                rank = rank +"★"
            if len(rank)==0:
                rank = '0'
            results_list.append({"title":resultsTitle,"rank":rank,"sentence":resultsSntns })

        return render_template("results.html", results=results_list , vector = isVector)

    else:
        
        q = parser.parse(query)
        with ix.searcher(weighting=weighting) as searcher:
            results = searcher.search(q)
            
            results_list = []
            for r in results:
                
                highlighted_text = r.highlights("content")
                results_list.append({"title": r["title"], "path": r["path"], "highlight": highlighted_text})

        
        return render_template("results.html", results=results_list)

        
        
        
        
        
        
        
        

        
        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
