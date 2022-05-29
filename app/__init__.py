from flask import Flask
from os import environ
import pymongo 

environ['FLASK_ENV'] = 'development'
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = environ['FLASK_SECRET_KEY'] if environ['FLASK_SECRET_KEY'] else 'my_secret_key'
app.config['HOST']  = environ['FLASK_DATABASE_HOST'] if environ['FLASK_DATABASE_HOST'] else 'localhost'
app.config['KAFKA'] = environ['KAFKA']
app.config['KAFKA_TOPIC'] = environ['KAFKA_TOPIC']

con = pymongo.MongoClient(f"mongodb://root:password@{app.config['HOST']}:27017/")
users_col = con['users']['users']

from app import routes