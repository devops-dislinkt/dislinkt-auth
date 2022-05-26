from flask import jsonify, request
from app import app, users_col
from app.models import User

@app.route('/')
def main():
    temp = 'world'
    return 'hello ' + temp

@app.route('/db')
def test_db():
    print('connecting')
    users_arr = []
    users = users_col.find()
    for user in users:
        print(user)
        users_arr.append(user)
    
    return jsonify(users_arr)

@app.post('/create-new-user')
def create_new_user():
    data = request.json
    print(f'data: {data}, {type(data)}')
    user = User(name=data['name'], 
                surname=data['surname'], 
                email=data['email']
                )

    # add to db
    response = users_col.insert_one(data)
    print(response.acknowledged, response.inserted_id)
    return jsonify("done")

