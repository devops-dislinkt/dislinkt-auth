from flask import jsonify, request, current_app, Blueprint, g
from datetime import datetime, timedelta
from app.models import User
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app.routes_utils import check_token, required_roles
import json
from kafka import KafkaProducer
from os import environ
from app import mongo_api

api = Blueprint('api', __name__)

try:
    producer = KafkaProducer(bootstrap_servers=[environ['KAFKA']],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
except:
    pass

@api.post('/users')
def create_new_user():
    data = request.json
    if not data.get('username') or not data.get('password'):   return 'did not receive username or password', 400 
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password)

    # add to db and check if username is unique
    try:
        mongo_api.collection('users').insert_one({
            '_id': user.username, 
            'password': user.password,
            'role': user.role})
        
        # TODO: podesiti kafku da posalje test topic ako je test env. 
        # Mislim da bi trebalo preuzeti vrednost nakon send funkcije i proveriti da li se send izvrsio.
        # Ako se send nije izvrsio treba da uhvatimo neki exception
        producer.send(current_app.config['KAFKA_TOPIC'], {'username': user.username})
        
    except DuplicateKeyError:
        return jsonify("username not unique"), 400
    
    return jsonify(user.username)


@api.get('/users')
@check_token
@required_roles(['admin'])
def get_all_users():
    users_documents = mongo_api.collection('users').find()
    users: list[dict] = [user_document for user_document in users_documents]
    for user in users: user['_id'] = str(user['_id'])
    return jsonify(users)


@api.get('/login')
def login_user():
    data = request.json
    if not data.get('username') or not data.get('password'):   return 'did not receive username or password', 400 
    username = data['username']
    password = data['password']

    # find user with username
    user:dict | User | None = mongo_api.collection('users').find_one({'_id': username})
    if not user: return f'not found user with username: {username}', 400
    user = User(username = user['_id'],
                password = user['password'],
                role = user['role'])
    
    # check password
    is_password_correct = check_password_hash(user.password, password)
    if not is_password_correct: return 'wrong password provided', 400

    token = jwt.encode({'username': user.username, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                        current_app.config['SECRET_KEY'],
                        algorithm='HS256')
    return token


@api.get('/is-token-valid')
@check_token
def is_token_valid():
    """ Function checks if token is valid. 
    No params, just pass bearer token in authentication header.
    The logic is already happening in @check_token decorator function.
    If everything is ok, return 200, otherwise error will be returned from @check_token.
    """

    return 'token is valid', 200