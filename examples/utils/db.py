from pymongo import MongoClient

MongoUrl = 'mongodb://localhost:27017/'


def get_db():
    client = MongoClient(MongoUrl)
    return client['dns-dos-sim']