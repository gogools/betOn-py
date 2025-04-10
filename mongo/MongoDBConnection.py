import certifi
import pymongo
from pymongo.server_api import ServerApi


class MongoDBConnection:

    def __init__(self, host='localhost', port=27017, uri=None):
        if uri is not None:
            self.client = pymongo.MongoClient(uri,
                                              tls=True,
                                              tlsCAFile=certifi.where(),
                                              tlsCertificateKeyFile="./mongo/beton_mongodb.pem",
                                              server_api=ServerApi('1'))
        else:
            self.client = pymongo.MongoClient(host, port)


    def get_database(self, db_name: str):
        return self.client[db_name]