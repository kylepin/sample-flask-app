

class BaseConfig:
    MONGO_DBNAME = 'books'
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017

class TestConfig(BaseConfig):
    MONGO_DBNAME = 'books-test'
    TESTING = True
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEVELOPMENT = True


app_config = {
    'test': TestConfig,
    'dev': DevelopmentConfig,
}
