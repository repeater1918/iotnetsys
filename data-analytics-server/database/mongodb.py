import pymongo
import os
from bson.objectid import ObjectId
from typing import Union, Dict, Tuple, List


MONGO_ATLAS_URI = f"mongodb+srv://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PWD')}@{os.getenv('MONGO_CLSTR')}"


class Database:
    def __init__(self, database_name: str):
        self.client = pymongo.MongoClient(MONGO_ATLAS_URI)
        self.database = self.client[database_name]

    def get_collection(self, collection_name):
        return self.database[collection_name]
    
    def get_node_collection_names(self) -> List[str]:
        names = [tbl for tbl in self.database.list_collection_names() if tbl[:4] == 'node']
        return names

    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def insert_many(self, collection_name, documents):
        collection = self.get_collection(collection_name)
        return collection.insert_many(documents)

    def find_one(self, collection_name, filter):
        collection = self.get_collection(collection_name)
        return collection.find_one(filter)

    def find(self, collection_name, filter):
        collection = self.get_collection(collection_name)
        return collection.find(filter)

    def update_one(self, collection_name, filter, update):
        collection = self.get_collection(collection_name)
        return collection.update_one(filter, update)

    def update_many(self, collection_name, filter, update):
        collection = self.get_collection(collection_name)
        return collection.update_many(filter, update)

    def delete_one(self, collection_name, filter):
        collection = self.get_collection(collection_name)
        return collection.delete_one(filter)

    def delete_many(self, collection_name, filter):
        collection = self.get_collection(collection_name)
        return collection.delete_many(filter)

    def find_by_pagination(
        self, collection_name: str, last_id: ObjectId, page_size: int, sessionid=None
    ) -> Union[Tuple[None, None], Tuple[List[Dict]], ObjectId]:
        collection = self.get_collection(collection_name)
        
        #print(f"Getting data from {collection_name} for this session {sessionid}")
        if sessionid is None:
            return None, None 
        
        if last_id is None:
            cursor = collection.find({"sessionid":sessionid}).limit(page_size)
        else:
            cursor = collection.find({"_id": {"$gt": last_id}, 
                                      "sessionid": {'$eq': sessionid}}).limit(page_size)
        
        # Get the data
        data = [x for x in cursor]

        if not data:
            # No documents left
            return None, None

        # Get last id
        last_id = max([x["_id"] for x in data])

        return data, last_id
    

    def find_session_id(self, collection_name: str):
        collection = self.get_collection(collection_name)
        sessionid = collection.distinct('sessionid')[-1]  #Get last session id       
        
        return sessionid
