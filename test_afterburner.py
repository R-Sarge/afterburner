# Afterburner tests
# test_afterburner.py

import pytest

from api import API

FILE_DIR = 'css'
FILE_NAME = 'main.css'
FILE_CONTENTS = 'body {background-color: #E0FCFF}'

# Helpers

def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)

    return asset

# Tests

def test_adding_basic_route(api):
    @api.route('/home')
    def home(request, response):
        response.text = 'TEST'

    with pytest.raises(AssertionError):
        @api.route('/home')
        def home2(request, response):
            response.text = 'TEST'

def test_client_test_request(api, client):
    RESPONSE_TEXT = 'Neato!'

    @api.route('/test')
    def test(request, response):
        response.text = RESPONSE_TEXT

    assert client.get('http://testserver/test').text == RESPONSE_TEXT

def test_parameter_route(api, client):
    @api.route('/{name}')
    def test(request, response, name):
        response.text = f'Sup {name}'

    assert client.get('http://testserver/user1').text == 'Sup user1'
    assert client.get('http://testserver/user2').text == 'Sup user2'

def test_default_404(client):
    response = client.get('http://testserver/doesnotexist')

    assert response.status_code == 404
    assert response.text == 'Not found'

def test_class_based_handler_get(api, client):
    RESPONSE_TEST = 'This is a GET request'

    @api.route('/books')
    class BooksResource:
        def get(self, request, response):
            response.text = RESPONSE_TEST

    assert client.get('http://testserver/books').text == RESPONSE_TEST

def test_class_based_handler_post(api, client):
    RESPONSE_TEST = 'This is a POST request'

    @api.route('/books')
    class BooksResource:
        def post(self, request, response):
            response.text = RESPONSE_TEST

    assert client.post('http://testserver/books').text == RESPONSE_TEST

def test_class_based_handler_put(api, client):
    RESPONSE_TEST = 'This is a PUT request'

    @api.route('/books')
    class BooksResource:
        def put(self, request, response):
            response.text = RESPONSE_TEST

    assert client.put('http://testserver/books').text == RESPONSE_TEST

def test_class_based_handler_delete(api, client):
    RESPONSE_TEST = 'This is a DELETE request'

    @api.route('/books')
    class BooksResource:
        def delete(self, request, response):
            response.text = RESPONSE_TEST

    assert client.delete('http://testserver/books').text == RESPONSE_TEST

def test_method_not_allowed(api, client):
    @api.route('/books')
    class BooksResource:
        def get(self, request, response):
            response.text = 'suuuup'

    with pytest.raises(AttributeError):
        client.post('http://testserver/books')

def test_adding_alternate_route(api, client):
    RESPONSE_TEXT = 'Adding Django style route'

    def home(request, response):
        response.text = RESPONSE_TEXT

    api.add_route('/alternate', home)

    assert client.get('http://testserver/alternate').text == RESPONSE_TEXT

def test_template(api, client):
    def html_handler(request, response):
        context_dict = {
            'title': 'Some title',
            'message': 'Some name',
        }

        response.body = api.template('index.html', context=context_dict)

    api.add_route('/html', html_handler)

    response = client.get('http://testserver/html')
    assert 'text/html' in response.headers['Content-type']
    assert 'Some title' in response.text
    assert 'Some name' in response.text

def test_custom_exception_handler(api, client):
    def on_exception(request, response, exception):
        response.text = 'AttributeErrorHappened'

    api.add_exception_handler(on_exception)

    @api.route('/')
    def index(request, response):
        raise AttributeError()

    response = client.get('http://testserver/')
    assert response.text == 'AttributeErrorHappened'

def test_nonexistent_static_file(api, client):
    assert client.get('http://testserver/main.css').status_code == 404

def test_static_content(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp('static')
    _create_static(static_dir)
    api = API(static_dir=str(static_dir))
    client = api.test_session()

    response = client.get(f'http://testserver/{FILE_DIR}/{FILE_NAME}')

    assert response.status_code == 200
    assert response.text == FILE_CONTENTS