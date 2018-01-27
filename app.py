from bson.errors import InvalidId
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, ObjectId
from jsonschema import validate, ValidationError

import config
from helpers import make_serializable

mongo = PyMongo()

def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    mongo.init_app(app)

    CREATE_BOOK_SCHEMA = {
        '$schema': 'http://json-schema.org/draft-06/schema#',
        'title': 'Book',
        'type': 'object',
        'properties': {
            'author': {'type': 'string'},
            'title': {'type': 'string'},
            'read_status': {'type': 'string',
                            'enum': ['read', 'reading', 'want-to-read']},
            'isbn': {'type': 'string'},
        },
        'required': ['author', 'title'],
        'additionalProperties': False,
    }

    UPDATE_BOOK_SCHEMA = {
        '$schema': 'http://json-schema.org/draft-06/schema#',
        'title': 'Book',
        'description': 'schema for updating a book document',
        'type': 'object',
        'properties': {
            'author': {'type': 'string'},
            'title': {'type': 'string'},
            'read_status': {'type': 'string',
                            'enum': ['read', 'reading', 'want-to-read']},
            'isbn': {'type': 'string'},
        },
        'additionalProperties': False,
    }

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
        try:
            validate(book, CREATE_BOOK_SCHEMA)
        except ValidationError as e:
            return 'ValidationError: {}'.format(e.message), 500

        book_id = books.insert(book)

        new_book = books.find_one({'_id': book_id})
        output = make_serializable(new_book)

        response = jsonify(output)
        response.status_code = 201
        return response

    @app.route('/books/<id>', methods=['GET'])
    def get_book(id):
        books = mongo.db.books

        try:
            book = books.find_one_or_404({'_id': ObjectId(id) })
        except InvalidId:
            return 'InvalidId: {} is not a valid ID'.format(id), 400
        output = make_serializable(book)

        return jsonify(output)

    @app.route('/books/<id>', methods=['DELETE'])
    def delete_book(id):
        books = mongo.db.books
        try:
            result = books.delete_one({'_id': ObjectId(id)})
        except InvalidId:
            return 'InvalidId: {} is not a valid ID'.format(id), 400

        if result.deleted_count == 1:
            return ('', 204)

        return ('', 404)

    return app

if __name__ == '__main__':
    app = create_app(config.DevelopmentConfig)
    app.run(debug=True)
