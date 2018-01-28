from flask import Flask
from flask_restful import Api

import config
from resources import BooksAPI, BooksCollectionAPI, IndexAPI, mongo

api = Api()
api.add_resource(IndexAPI, '/', endpoint='index')
api.add_resource(BooksCollectionAPI, '/books', endpoint='books')
api.add_resource(BooksAPI, '/books/<string:id>', endpoint='book')


def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    mongo.init_app(app)
    api.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app(config.DevelopmentConfig)
    app.run(debug=True)
