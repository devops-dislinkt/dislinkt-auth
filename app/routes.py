from flask import jsonify, request, current_app, Blueprint, g, Response
from datetime import datetime, timedelta
from app.models import User
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from kafka import KafkaProducer
from os import environ
from app import mongo_api

api = Blueprint('api', __name__)
from .routes_utils import check_token, required_roles


producer = KafkaProducer(bootstrap_servers=[environ['KAFKA']],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@api.post('/auth/users')
def create_new_user():
    data = request.json
    if not data.get('username') or not data.get('password'): 
        return 'did not receive username or password', 400 
    
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password)

    # add to db and check if username is unique
    try:
        mongo_api.collection('users').insert_one({
            '_id': user.username, 
            'password': user.password,
            'role': user.role})
        producer.send(current_app.config['KAFKA_TOPIC'], {'username': user.username})
        
    except DuplicateKeyError:
        return jsonify("username not unique"), 400
    
    return jsonify(user.username)


@api.get('/auth/users')
@check_token
@required_roles(['admin'])
def get_all_users():
    users_documents = mongo_api.collection('users').find()
    users: list[dict] = [user_document for user_document in users_documents]
    for user in users: user['_id'] = str(user['_id'])
    return Response(jsonify(users))


@api.post('/auth/login')
def login_user():
    data = request.json
    if not data.get('username') or not data.get('password'): 
        return 'did not receive username or password', 400 
    
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

    token = jwt.encode({'username': user.username, 'role': user.role, 'exp': datetime.utcnow() + timedelta(minutes=30)},

                        current_app.config['SECRET_KEY'],
                        algorithm='HS256')
    return jsonify(token)


@api.get('/auth/is-token-valid')
@check_token
def validate_token():
    """ Function checks if token is valid. 
    No params, just pass bearer token in authentication header.
    The logic is already happening in @check_token decorator function.
    If everything is ok, return 200, otherwise error will be returned from @check_token.
    """
    
    return  Response('token is valid')

@api.put('/users/username')
@check_token
def edit_profile_username():
    token = request.headers['authorization'].split(' ')[1]
    user: dict | None = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user =  mongo_api.collection('users').find_one({'_id': user['username']})
    
    if not user: return 'user not found', 400
    if not request.json.get('old_username') or not request.json.get('new_username'): 
        return 'did not receive username or password', 400 
    
    old_username = request.json.get('old_username')
    new_username = request.json.get('new_username')
    
    if old_username != user['_id']: return 'old_username not correct', 400

    user['_id'] = new_username # set new _id
    mongo_api.collection('users').insert_one(user) # insert with new _id
    mongo_api.collection('users').delete_one({'_id': old_username})

    producer.send(current_app.config['KAFKA_TOPIC'], 
                {'username': old_username, 'new_username': new_username})

    return jsonify(request.json.get('new_username'))
