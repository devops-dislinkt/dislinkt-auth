from flask import Flask
from os import environ
import pymongo 
environ['FLASK_ENV'] = 'development'
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

con = pymongo.MongoClient("mongodb://root:password@db:27017/")
db = con['probadb']
print(con.list_database_names())
    
from app import routes