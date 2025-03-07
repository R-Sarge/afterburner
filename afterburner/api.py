# Afterburner framework
# api.py

import os
import inspect

from parse import parse
from webob import Request
from requests import Session as RequestSession
from wsgiadapter import WSGIAdapter as RequestWSGIAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise

from .response import Response
from .middleware import Middleware

class API:
    def __init__(self, template_dir='templates', static_dir='assets/css/'):
        self.routes = {}
        self.exception_handler = None
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(template_dir))
        )
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir, prefix='/static')
        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        """
        WSGI entrypoint
        """
        path_info = environ["PATH_INFO"]

        # Direct /static API calls to WhiteNoise
        if path_info.startswith('/static'):
            return self.whitenoise(environ, start_response)

        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        """
        WSGI app creation
        """
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def add_middleware(self, middleware_cls):
        """
        Add new middleware class to the stack
        """
        self.middleware.add(middleware_cls)

    def template(self, template_name, context=None):
        """
        Returns and renders specified Jinja2 template (template_name)
        from specified root directory (template_dir)
        """
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context)

    def add_route(self, path, handler, allowed_methods=None):
        """
        Adds a path to the URI resources,
        and associates a handler to the path.
        """
        assert path not in self.routes, f'Duplicate route, {path}'

        if allowed_methods is None:
            allowed_methods = ['get', 'head', 'post', 'put', 'delete', 'connect', 'options', 'trace', 'patch']

        self.routes[path] = {'handler': handler, 'allowed_methods': allowed_methods}

    def route(self, path, allowed_methods=None):
        """
        @decorator
        Adds a path to the URI resources,
        and associates a handler to the path.
        """
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def find_handler(self, request_path):
        """
        Returns handler associated with requested path.
        """
        for path, handler_data in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler_data, parse_result.named

        return None, None

    def default_response(self, response):
        """
        Default response handler
        """
        response.status_code = 404
        response.text = 'Not found'

    def handle_request(self, request):
        """
        Framework request handler
        """
        response = Response()

        handler_data, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler_data is not None:
                handler = handler_data['handler']
                allowed_methods = handler_data['allowed_methods']

                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError('Method not allowed', request.method)
                else:
                    if request.method.lower() not in allowed_methods:
                        raise AttributeError('Method not allowed', request.method)

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
        """
        Adds a custom exception handler
        """
        self.exception_handler = exception_handler

    def test_session(self, base_url='http://testserver'):
        """
        Test session used for testing
        """
        session = RequestSession()
        session.mount(prefix=base_url, adapter=RequestWSGIAdapter(self))
        return session