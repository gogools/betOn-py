import os

import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from mongo.WhoScoredDAO import WhoScoredDAO
from util import msg


def init(host='localhost', port=27017):
    beton_db = "mongodb+srv://betondb.zfvkpn5.mongodb.net/?authSource=$external&authMechanism=MONGODB-X509"
    dao = WhoScoredDAO(uri=beton_db, db_name="betondb")

    msg(f"MongoDB beton db collections: {dao.get_all_collections()}")
    msg(f"MongoDB beton db databases: {dao.get_all_databases()}")

def crud():
    beton_db = "mongodb+srv://betondb.zfvkpn5.mongodb.net/?authSource=$external&authMechanism=MONGODB-X509"
    dao = WhoScoredDAO(uri=beton_db, db_name="betondb")

    # Insert document
    document = {
        "name": "John",
        "age": 25,
        "city": "New York"
    }
    dao.insert_document("users", document)

    # Read document
    query = {"name": "John"}
    for doc in dao.read_document("users", query):
        msg(doc)

    # Update document
    _filter = {"name": "John"}
    update = {"$set": {"age": 26}}
    dao.update_document("users", _filter, update)

    # Delete document
    dao.delete_document("users", query)

if __name__ == "__main__":
    current_dir = os.getcwd()
    print(current_dir)
    init()
