from flask import jsonify, request
from app import app, db

@app.route('/')
def main():
    temp = 'world'
    return 'hello ' + temp

@app.route('/db')
def test_db():
    print('connecting')
    users_arr = []
    users = db['users'].find()
    for user in users:
        print(user)
        users_arr.append(user)
    
    return jsonify(users_arr)
