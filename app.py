# Afterburner framework
# app.py

from api import API

API_BASE = '/api'
APP_VARS = {
    'title': 'Afterburner'
}

app = API()

def custom_exception_handler(request, response, exception_cls):
    exception_str = str(exception_cls)

    response.text = exception_str
    response.body = app.template(
        'error.html',
        context = {
            'title': APP_VARS['title'],
            'error': exception_str,
        }
    )

app.add_exception_handler(custom_exception_handler)

@app.route(API_BASE + '/home')
def home(request, response):
    response.text = 'Home API'

@app.route(API_BASE + '/about')
def about(request, response):
    response.text = 'About API'

@app.route(API_BASE + '/reverse/{name}')
def greet(request, response, name):
    output = name
    output += '<br>' + name[::-1]

    response.text = output

@app.route(API_BASE + '/books')
class BooksResource:
    def post(self, request, response):
        response.text = "Endpoint to CREATE a book\n"

    def get(self, request, response):
        response.text = "Endpoint to RETRIEVE a book\n"

    def delete(self, request, response):
        response.text = "Endpoint to DELETE and book\n"

    """
    def put(self, request, response):
        response.text = "Endpoint to UPDATE a book\n"
    """

@app.route(API_BASE + '/sample')
def sample(request, response):
    output = 'Sample API'
    response.text = output

@app.route('/template')
def template(request, response):
    response.body = app.template(
        'index.html',
        context = {
            'title': APP_VARS['title'],
            'message': 'The cool Python framework.'
        }
    )

@app.route(API_BASE + '/exception')
def throw_exception(request, response):
    raise AssertionError('This handler should not be used')