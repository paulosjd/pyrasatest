from collections import namedtuple

from pyramid import testing

from .mock_db_session import MockDbSession


class DummyTmplContext:

    def set_data(self, dct):
        self.__dict__.update(dct)

    def __setattr__(self, key, value):
        self.__dict__[key] = value


class MockRequest(testing.DummyRequest):
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.dbsession = MockDbSession()
        self.tmpl_context = DummyTmplContext()
        self.mock_route_path = '/foo/bar'

    def route_url(self, view_path, **kwargs):
        if view_path == 'shared.info':
            return 'info/index'

    def static_url(self, *args, **kwargs):
        return 'static_url_return_val'

    def route_path(self, *args, **kwargs):
        return self.mock_route_path


class MockSession(testing.DummySession):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save_called = False

    def save(self):
        self.save_called = True


class MockResponse:
    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs
        self.headers = {}

    def set_cookie(self, *args, **kwargs):
        pass
