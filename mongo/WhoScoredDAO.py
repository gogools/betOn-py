from mongo.MongoDBConnection import MongoDBConnection
from util import msg


class WhoScoredDAO:

    def __init__(self, host:str ="localhost", port:int =27017, uri:str =None, db_name:str =None):
        if uri is not None:
            self.db = MongoDBConnection(uri=uri).get_database(db_name)
        else:
            self.db = MongoDBConnection(host, port).get_database(db_name)


    def get_all_collections(self):
        return self.db.list_collection_names()


    def get_all_databases(self):
        return self.db.client.list_database_names()


    def read_document(self, collection_name:str, query:dict):
        collection = self.db[collection_name]
        return collection.find(query)


    def insert_document(self, collection_name:str, document:dict) -> bool:
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        msg(f"Inserted document with ID: {result.inserted_id} of collection {collection_name}")
        return result.acknowledged


    def update_document(self, collection_name:str, _filter:dict, update:dict) -> bool:
        collection = self.db[collection_name]
        result = collection.update_one(_filter, update)
        msg(f"Modified {result.modified_count} document(s) of collection {collection_name}")
        return result.acknowledged


    def delete_document(self, collection_name:str, query:dict) -> bool:
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        msg(f"Deleted {result.deleted_count} document(s) of collection {collection_name}")
        return result.acknowledged
