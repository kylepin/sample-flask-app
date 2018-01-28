import json
import unittest

from app import create_app, mongo
import config

URL = ''
BOOKS_COLLECTION_API_URL = '{}/books'.format(URL)
BOOKS_API_URL = '{}/{{}}'.format(BOOKS_COLLECTION_API_URL)
HEADERS = {'content-type': 'application/json'}


class TestBooksAPIBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config.TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def tearDown(self):
        mongo.db.books.remove({})


class TestIndex(TestBooksAPIBase):
    def test_index_page(self):
        response = self.client.get('/')
        self.assertEquals(200, response.status_code)
        self.assertEquals(b'"Welcome to my RESTful API"\n', response.data)


class TestGetBooksCollection(TestBooksAPIBase):
    def test_no_documents(self):
        response = self.client.get(BOOKS_COLLECTION_API_URL)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.data), [])

    def test_get_collection_with_contents(self):
        documents_to_insert = [
            {'author': 'CS Lewis', 'title': 'Screwtape Letters'},
            {'author': 'CS Lewis', 'title': 'Chronicles of Narnia'},
            {'author': 'CS Lewis', 'title': 'The Great Divorce'},
            {'author': 'CS Lewis', 'title': 'The Weight of Glory'},
        ]
        mongo.db.books.insert_many(documents_to_insert)

        for doc in documents_to_insert:
            doc['_id'] = str(doc['_id'])

        expected_documents = sorted(documents_to_insert,
                                    key=lambda doc: doc['_id'])

        response = self.client.get(BOOKS_COLLECTION_API_URL)
        self.assertEquals(response.status_code, 200)

        returned_documents = json.loads(response.data)
        returned_documents = sorted(returned_documents,
                                    key=lambda doc: doc['_id'])

        self.assertListEqual(expected_documents, returned_documents,
                             'The returned documents did not match the '
                             'documents inserted.')

        ids_to_delete = [doc['_id'] for doc in expected_documents]
        mongo.db.books.remove({'_id': {'$in': ids_to_delete}})


class TestBooksPost(TestBooksAPIBase):
    def test_add_book_with_minimum_fields(self):
        """Test adding a book with minimum fields, author and title."""
        payload = {
            'author': 'Michael G Scott',
            'title': 'Somehow I Manage',
        }
        response = self.client.post(BOOKS_COLLECTION_API_URL, headers=HEADERS,
                                    data=json.dumps(payload))
        returned_book = json.loads(response.data)

        book_id = returned_book['_id']
        del returned_book['_id']

        self.assertDictEqual(payload, returned_book,
                             'Book returned in response from API did not '
                             'match the payload.')

        mongo.db.books.remove({'_id': book_id})

    def test_add_book_with_all_fields(self):
        """Test adding a book with all fields, author, title, isbn, read
        status."""
        payload = {
            'author': 'Michael G Scott',
            'title': 'Somehow I Manage',
            'read_status': 'want-to-read',
            'isbn': '9781463586621'
        }
        response = self.client.post(BOOKS_COLLECTION_API_URL, headers=HEADERS,
                                    data=json.dumps(payload))
        returned_book = json.loads(response.data)

        book_id = returned_book['_id']
        del returned_book['_id']

        self.assertDictEqual(payload, returned_book,
                             'Book returned in response from API did not match'
                             'the payload.')

        mongo.db.books.remove({'_id': book_id})

    def test_add_book_with_missing_field(self):
        """Test adding a book with the author field missing."""
        payload = {
            'title': 'Somehow I Manage',
        }

        response = self.client.post(BOOKS_COLLECTION_API_URL, headers=HEADERS,
                                    data=json.dumps(payload))
        self.assertEqual(500, response.status_code,
                         'Failed to catch missing author field.')

        payload = {'author': 'Michael G Scott'}
        response = self.client.post(BOOKS_COLLECTION_API_URL, headers=HEADERS,
                                    data=json.dumps(payload))
        self.assertEqual(500, response.status_code,
                         'Failed to catch missing title field.')

    def test_add_book_with_extra_field(self):
        """Test adding a book with an extra field."""
        payload = {
            'author': 'Michael G Scott',
            'title': 'Somehow I Manage',
            'asdf': 'asdf asdf asdf',
        }

        response = self.client.post(BOOKS_COLLECTION_API_URL, headers=HEADERS,
                                    data=json.dumps(payload))
        self.assertEqual(500, response.status_code,
                         'Failed to catch extra, unvalidated field.')


class TestBooksGet(TestBooksAPIBase):
    def test_get_book(self):
        book = {
            'author': 'Michael G Scott',
            'title': 'Somehow I Manage',
            'read_status': 'want-to-read',
            'isbn': '9781463586621'
        }
        mongo.db.books.insert_one(book)

        url = BOOKS_API_URL.format(book['_id'])
        response = self.client.get(url)

        book['_id'] = str(book['_id'])

        self.assertEqual(200, response.status_code)

        returned_book = json.loads(response.data)
        self.assertEqual(book, returned_book)

        mongo.db.books.delete_one({'_id': book['_id']})

    def test_get_nonexistent_book(self):
        id = '5a6cbc261d242f09ad6bed33'
        url = BOOKS_API_URL.format(id)

        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_get_book_invalid_id(self):
        id = '12345'
        url = BOOKS_API_URL.format(id)

        response = self.client.get(url)
        self.assertEqual(400, response.status_code)


class TestBooksDelete(TestBooksAPIBase):
    def test_delete_book(self):
        """Test deleting a book."""
        book = {
            'author': 'Michael G Scott',
            'title': 'Somehow I Manage',
            'read_status': 'want-to-read',
            'isbn': '9781463586621'
        }
        mongo.db.books.insert_one(book)

        url = BOOKS_API_URL.format(book['_id'])
        response = self.client.delete(url)

        self.assertEqual(
            204, response.status_code,
            'Deleting "_id": {} was unsuccessful'.format(book['_id']))

    def test_delete_nonexistent_book(self):
        """Test deleting a book that does not exist."""
        id = '5a6cbc261d242f09ad6bed33'
        url = BOOKS_API_URL.format(id)
        response = self.client.delete(url)

        self.assertEqual(404, response.status_code,
                         'Failed to respond with 404 status code.')

    def test_delete_invalid_id(self):
        """Test what happens when I pass an invalid ID."""
        id = '12345'
        url = BOOKS_API_URL.format(id)
        response = self.client.delete(url)

        self.assertEqual(400, response.status_code,
                         'Failed to respond with 400 status code.')
