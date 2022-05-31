import pytest
from app import create_app, mongo_api
from app.models import User 
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

# constants
TEST_DB = 'test_db'
USER_VALID = User(username='test_djura', password='test_djura123')
USER_INVALID_PASS = User(username='test_djura', password='wrong_password')
USER_INVALID_USERNAME = User(username='test_niko', password='test_niko')
USER_NEW = User(username='test_pera', password='test_pera123')

# helper methods for database
def setup_db():
    '''setup database before tests start executing'''
    # reroute traffic to test database
    mongo_api.database = mongo_api.connection[TEST_DB]
    # empty test db just in case
    mongo_api.connection.drop_database(TEST_DB)

    # insert dummy data for tests
    mongo_api.collection('users').insert_many([
        {'_id': 'test_admin', 'password':generate_password_hash('test_admin'), 'role': 'admin'},
        {'_id': 'test_djura', 'password':generate_password_hash('test_djura123'), 'role': 'user'},
        {'_id': 'test_mika', 'password':generate_password_hash('test_mika123'), 'role': 'user'},
        {'_id': 'test_mina', 'password':generate_password_hash('test_mina123'), 'role': 'user'},
    ])

def teardown_db():
    '''destroy testing database and all of its content after tests finished.'''
    mongo_api.connection.drop_database(TEST_DB)

@pytest.fixture(scope='module')
def client() -> FlaskClient:
    '''
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    '''
    # setup
    app = create_app('test')
    setup_db()
    
    with app.test_client() as client:
        yield client
    
    # teardown
    teardown_db()
    


class TestClassCreateUser:
    '''Test case for creating user (adding new users to the system).'''

    def test_create_user_success(self, client: FlaskClient):
        response = client.post('/api/users', json={'username': USER_NEW.username, 'password': USER_NEW.password})
        assert response.json == USER_NEW.username
        assert response.status_code == 200

    def test_create_user_without_username(self, client: FlaskClient):
        response = client.post('/api/users', json={ 'password':USER_NEW.password})
        msg = response.data.decode('UTF-8')
        assert 'did not receive username or password' == msg
        assert response.status_code == 400

    def test_create_user_with_existing_username(self, client: FlaskClient):
        response = client.post('/api/users', json={'username': USER_VALID.username, 'password': USER_INVALID_PASS.password})
        assert 'username not unique' == response.json
        assert response.status_code == 400
        

class TestClassToken:
    '''Test case for creating user token.'''

    def test_is_token_valid_without_token(self, client:FlaskClient):
        response = client.get('/api/is-token-valid')
        msg = response.json['message']
        assert 'No token provided' == msg
        assert response.status_code == 400

    def test_is_token_valid_with_wrong_token(self, client:FlaskClient):
        response = client.get('/api/is-token-valid', headers={'authorization': 'Bearer 12345asdfg'})
        msg = response.data.decode('UTF-8')
        assert 'Invalid token. Please log in again.' == msg
        assert response.status_code == 400

    def test_is_token_valid_with_good_token(self, client:FlaskClient):
        # first login
        login_response = client.get('/api/login', json = {'username': USER_VALID.username, 'password': USER_VALID.password})
        token = login_response.data.decode('UTF-8')
        response = client.get('/api/is-token-valid', headers={'authorization': f'Bearer {token}'})
        msg = response.data.decode('UTF-8')
        assert 'token is valid' == msg
        assert response.status_code == 200


class TestClassLogin:
    '''Test case for when user logs in.'''

    def test_login_success(self, client: FlaskClient):
        response = client.get('/api/login', json = {'username': USER_VALID.username, 'password': USER_VALID.password})
        assert response.status_code == 200

    def test_login_with_wrong_username(self, client: FlaskClient):
        response = client.get('/api/login', json = {'username': USER_INVALID_USERNAME.username, 'password': USER_INVALID_USERNAME.password})
        assert 'not found user' in response.data.decode('UTF-8')
        assert response.status_code == 400

    def test_login_with_wrong_password(self, client: FlaskClient):
        response = client.get('/api/login', json = {'username': USER_INVALID_PASS.username, 'password': USER_INVALID_PASS.password})
        assert 'wrong password provided' == response.data.decode('UTF-8')
        assert response.status_code == 400

    def test_login_without_password(self, client: FlaskClient):
        response = client.get('/api/login', json = {'username': USER_VALID.username})
        assert 'did not receive username or password' == response.data.decode('UTF-8')
        assert response.status_code == 400
