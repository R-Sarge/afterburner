# Afterburner framework
# api.py

import os
import inspect

from parse import parse
from webob import Request, Response
from requests import Session as RequestSession
from wsgiadapter import WSGIAdapter as RequestWSGIAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise

class API:
    def __init__(self, template_dir='templates', static_dir='assets/css/'):
        self.routes = {}
        self.exception_handler = None
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(template_dir))
        )
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

    def __call__(self, environ, start_response):
        return self.whitenoise(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def template(self, template_name, context=None):
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context).encode()

    def add_route(self, path, handler):
        assert path not in self.routes, f'Duplicate route, {path}'

        self.routes[path] = handler

    def route(self, path):
        """
        Add route decorator
        """
        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named

        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text = 'Not found'

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method not allowed", request.method)

                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    def test_session(self, base_url='http://testserver'):
        session = RequestSession()
        session.mount(prefix=base_url, adapter=RequestWSGIAdapter(self))
        return session