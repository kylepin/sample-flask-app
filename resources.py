from bson.errors import InvalidId
from flask import jsonify, request
from flask_pymongo import ObjectId, PyMongo
from flask_restful import Resource
from jsonschema import validate, ValidationError

from helpers import make_serializable

mongo = PyMongo()

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


class IndexAPI(Resource):
    def get(self):
        return 'Welcome to my RESTful API'


class BooksCollectionAPI(Resource):
    def get(self):
        books = mongo.db.books
        output = []
        for book in books.find():
            output.append(make_serializable(book))

        return jsonify(output)

    def post(self):
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


class BooksAPI(Resource):
    def get(self, id):
        books = mongo.db.books

        try:
            book = books.find_one_or_404({'_id': ObjectId(id)})
        except InvalidId:
            return 'InvalidId: {} is not a valid ID'.format(id), 400
        output = make_serializable(book)

        return jsonify(output)

    def delete(self, id):
        books = mongo.db.books
        try:
            result = books.delete_one({'_id': ObjectId(id)})
        except InvalidId:
            return 'InvalidId: {} is not a valid ID'.format(id), 400

        if result.deleted_count == 1:
            return ('', 204)

        return ('', 404)
