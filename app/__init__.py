from flask import Flask
from os import environ
import pymongo 
environ['FLASK_ENV'] = 'development'
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

host = getattr(environ, 'FLASK_DATABASE_HOST', 'localhost')
con = pymongo.MongoClient(f"mongodb://root:password@{host}:27017/")
db = con['probadb']
print(con.list_database_names())
    
from app import routes