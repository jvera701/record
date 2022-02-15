from flask import jsonify, Flask, request, abort
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson import json_util 
from bson.objectid import ObjectId
import re

# Taken from https://stackoverflow.com/questions/60785345/pymongo-best-way-to-remove-oid-in-response
def remove_oid(string):
    while True:
        pattern = re.compile('{\s*"\$oid":\s*(\"[a-z0-9]{1,}\")\s*}')
        match = re.search(pattern, string)
        if match:
            string = string.replace(match.group(0), match.group(1))
        else:
            return string

load_dotenv()
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)
CONNECTION = os.getenv('CONNECTION')

@app.route("/")
def get_documents():
    with MongoClient(CONNECTION) as client:
        db = client.record.record
        documents = [ doc for doc in db.find()]
        return remove_oid( json_util.dumps({'documents' : documents}) )

@app.route("/", methods=['POST'])
def new_document():
    content = request.json
    with MongoClient(CONNECTION) as client:
        db = client.record.record
        result = db.insert_one(content).inserted_id
        document = db.find_one({"_id" : result})
        return remove_oid( json_util.dumps({'document' : document}))

@app.route("/", methods=['DELETE'])
def delete_document():
    content = request.json

    try:
        with MongoClient(CONNECTION) as client:
            id = content["_id"]     
            db = client.record.record
            db.delete_one({"_id": ObjectId(id)})

    except Exception:
        abort(jsonify(message="Document not found"), 404)
    
    return jsonify("ok"), 200

@app.route("/", methods=['PUT'])
def update_document():
    content = request.json
    with MongoClient(CONNECTION) as client:
        db = client.record.record
        id = content["_id"]
        content.pop("_id", None)
        db.update_one({"_id": ObjectId(id)}, 
        { "$set": content})
        document = db.find_one({"_id": ObjectId(id)})
        return remove_oid( json_util.dumps({'document' : document}))