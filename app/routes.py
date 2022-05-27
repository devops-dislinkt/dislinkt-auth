from flask import jsonify, request
from app import app, users_col
from app.models import User
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def main():
    temp = 'world'
    return 'hello ' + temp

@app.post('/users')
def create_new_user():
    data = request.json
    print(f'data: {data}')
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_password)

    # add to db and check if username is unique
    try:
        users_col.insert_one({
            '_id': user.username, 
            'username': user.username,
            'password': user.password})
    except DuplicateKeyError:
        return jsonify("username not unique"), 400
    
    return jsonify(user.username)


@app.get('/users')
def get_all_users():
    users_documents = users_col.find()
    users: list[dict] = [user_document for user_document in users_documents]
    for user in users: user['_id'] = str(user['_id'])
    return jsonify(users)