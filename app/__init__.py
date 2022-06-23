from typing import Literal
from app.MongoApi import MongoApi
from flask import Flask, g
from os import environ
from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient

mongo_api = MongoApi(None, None)


def create_app(env: Literal["prod", "test"] = "prod"):
    from . import routes

    # environ['FLASK_ENV'] = 'development'
    flask_app = Flask(__name__)

    flask_app.config["JSON_AS_ASCII"] = False
    flask_app.config["SECRET_KEY"] = (
        environ["FLASK_SECRET_KEY"]
        if "FLASK_SECRET_KEY" in environ
        else "my_secret_key"
    )
    flask_app.config["HOST"] = (
        environ["FLASK_DATABASE_HOST"]
        if "FLASK_DATABASE_HOST" in environ
        else "localhost"
    )
    flask_app.config["KAFKA"] = environ["KAFKA"]
    flask_app.config["KAFKA_TOPIC"] = environ["KAFKA_TOPIC"]

    DATABASE_CONNECTION_URI = (
        f"mongodb://root:password@{flask_app.config['HOST']}:27017/"
    )

    with flask_app.app_context():
        # setup connection
        con = MongoClient(DATABASE_CONNECTION_URI)
        mongo_api.connection = con

        # set users collection with test database if in test envinronment.
        if env == "test":
            flask_app.config["TESTING"] = True
            mongo_api.database = con["test_db"]
        else:
            mongo_api.database = con["users"]

        flask_app.register_blueprint(routes.api, url_prefix="/api")

    return flask_app
