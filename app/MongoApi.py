from dataclasses import dataclass
from pymongo.mongo_client import MongoClient
from pymongo.database import Database

@dataclass
class MongoApi:
    connection: MongoClient
    database: Database

    def collection(self, name:str):
        return self.database[name]
