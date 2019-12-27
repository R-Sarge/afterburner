# Afterburner framework
# middleware.py

from webob import Request

class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """
        WSGI entrypoint
        """
        request = Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)

    def add(self, middleware_cls):
        self.app = middleware_cls(self.app)

    def process_request(self, request):
        """
        Method to process a request.
        Should be overwritted in child implementation.
        """
        pass

    def process_response(self, request, response):
        """
        Method to process a response.
        Should be overwritted in child implementation.
        """
        pass

    def handle_request(self, request):
        """
        """
        # Process request
        self.process_request(request)

        # Send to app framework
        response = self.app.handle_request(request)

        # Process response
        self.process_response(request, response)
        return response