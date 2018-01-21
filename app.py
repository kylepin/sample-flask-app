from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from jsonschema import validate

import config
from helpers import make_serializable

logger = app.logger
app = Flask(__name__)

app.config['MONGO_DBNAME'] = config.MONGO_DBNAME
mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return "Welcome to my RESTful API"

@app.route('/books', methods=['GET'])
def get_books():
    books = mongo.db.books
    output = []
    for book in books.find():
        output.append(make_serializable(book))

    return jsonify(output)

#  request must contain Content-Type: application/json or request.json will not work as expected
@app.route('/books', methods=['POST'])
def add_book():
    books = mongo.db.books
    book = request.json
    validate(book)
    book_id = books.insert({
    'author': book['author'],
    'title': book['title'],
    'read_status': book['read_status'],
    'isbn': book['isbn'],
    })

    new_book = books.find_one({'_id': book_id})
    output = make_serializable(new_book)

    response = jsonify(output)
    response.status_code = 201
    return response

@app.route('/books/<id>', methods=['GET'])
def get_book(id):
    books = mongo.db.books

    book = books.find_one_or_404({'_id': id })
    output = make_serializable(book)

    return jsonify(output)

@app.route('/books/<id>', methods=['PUT'])
def update_book(id):
    books = mongo.db.books

    book = {}
    for key, book_attribute in request.json.items():
        book[key] = book_attribute
    books.update_one(
    {'_id': id },
    {'$set': book},
    )

    updated_book = books.find_one_or_404({'_id': id})
    output = make_serializable(updated_book)

    return jsonify(output)

@app.route('/books/<id>', methods=['DELETE'])
def delete_book(id):
    books = mongo.db.books

    result = books.delete_one({'_id': id})

    if result.deleted_count == 1:
        return ('',200)

    return ('',404)
