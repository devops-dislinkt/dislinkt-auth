from flask import request, current_app
from functools import wraps
from app.models import User
import jwt
from app import mongo_api
from .routes import api

def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'): 
            return {'message': 'No token provided'}, 400
    
        try:
            # verify token
            token = request.headers['authorization'].split(' ')[1]
            user = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            found_user = mongo_api.collection('users').find_one({'_id': user['username']})

            if not found_user: return f'not found user with username: {user["username"]}', 400

        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 400
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 400
        except:
            return 'Problem with authentication.', 400

        return f(*args, **kwargs)
    return wrap


def required_roles(roles: list[str]):
    def decorator_required_roles(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            try:
                # verify token
                token = request.headers['authorization'].split(' ')[1]
                user:dict | None | User = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                
                 # find user with username
                found_user = mongo_api.collection('users').find_one({'_id': user['username']})
                if not user: return f'not found user with username: {found_user["username"]}', 400
                user = User(username = user['_id'],
                            password = user['password'],
                            role = user['role'])
                
                if user.role not in roles: 
                    return f'provided role: {user.role}. Accepted roles: {roles}', 400
                    
            except:
                return 'Problem with auth.', 400

            return f(*args, **kwargs)
        return wrap
    return decorator_required_roles


# allow all origin
@api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    return response