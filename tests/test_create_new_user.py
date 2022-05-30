import pytest
from app import app, users_col
from app.models import User 
from flask.testing import FlaskClient



@pytest.fixture
def client() -> FlaskClient:
    '''
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    '''
    # print('******************setup')
    app.config['TESTING'] = True
    # override users collection. Reroute from 'users' database to 'test_db' database, which is used only for testing purposes.
    with app.test_client() as client:
        
        yield client
    
    # print('******************teardown')
    


class TestClassCreateUser:
    def setup(self):
        self.user = User(username='milan', password='milan123')
    
    def teadrown(self):
        users_col.delete_one({'_id': self.user.username})

    def test_create_user_success(self, client: FlaskClient):
        self.setup()
        response = client.post('/users', json={'username': self.user.username, 'password':self.user.password})
        assert response.json == 'milan'
        assert response.status_code == 200
        self.teadrown()

    def test_create_user_without_username(self, client: FlaskClient):
        self.setup()
        response = client.post('/users', json={ 'password':self.user.password})
        msg = response.data.decode('UTF-8')
        assert 'did not receive username or password' == msg
        assert response.status_code == 400
        self.teadrown()

    def test_create_user_with_existing_username(self, client: FlaskClient):
        response = client.post('/users', json={'username': 'nikola', 'password':'nikola123'})
        assert 'username not unique' == response.json
        assert response.status_code == 400
        

class TestClassToken:

    def test_is_token_valid_without_token(self, client:FlaskClient):
        response = client.get('/is-token-valid')
        msg = response.json['message']
        assert 'No token provided' == msg
        assert response.status_code == 400

    def test_is_token_valid_with_wrong_token(self, client:FlaskClient):
        response = client.get('/is-token-valid', headers={'authorization': 'Bearer 12345asdfg'})
        msg = response.data.decode('UTF-8')
        assert 'Invalid token. Please log in again.' == msg
        assert response.status_code == 400

    def test_is_token_valid_with_good_token(self, client:FlaskClient):
        # first login
        login_response = client.get('/login', json = {'username': 'nikola', 'password': 'nikola123'})
        token = login_response.data.decode('UTF-8')
        response = client.get('/is-token-valid', headers={'authorization': f'Bearer {token}'})
        msg = response.data.decode('UTF-8')
        assert 'token is valid' == msg
        assert response.status_code == 200


class TestClassLogin:

    def test_login_success(self, client: FlaskClient):
        response = client.get('/login', json = {'username': 'nikola', 'password': 'nikola123'})
        print(response.data, response.status_code)
        assert response.status_code == 200

    def test_login_with_wrong_username(self, client: FlaskClient):
        response = client.get('/login', json = {'username': 'johndoe', 'password': 'nikola123'})
        assert 'not found user' in response.data.decode('UTF-8')
        assert response.status_code == 400

    def test_login_with_wrong_password(self, client: FlaskClient):
        response = client.get('/login', json = {'username': 'nikola', 'password': 'wrong_password'})
        assert 'wrong password provided' == response.data.decode('UTF-8')
        assert response.status_code == 400

    def test_login_without_password(self, client: FlaskClient):
        response = client.get('/login', json = {'username': 'nikola'})
        assert 'did not receive username or password' == response.data.decode('UTF-8')
        assert response.status_code == 400
