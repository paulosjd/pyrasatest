from collections import namedtuple

from pyramid import testing
from sqlalchemy import exc

from .sqlalchemy_mocks import MockQuery


class MockDbSession:
    """
    Usage examples
    --------------
    raise SQLAlchemyError from self.request.dbsession.query(...).one()
        self.view.request.dbsession.mock_query_kwargs = {'raise_exc': SQLAlchemyError}
    """
    def __init__(self, mock_query_kwargs=None, **kwargs):
        self.mock_query_kwargs = mock_query_kwargs or {}
        self.return_value = None
        self.side_effect = None
        self.query_args = []
        self.query_call_count = 0
        self.added_records = []
        self.commit_called = False
        self.rollback_called = False
        self.raise_exception = kwargs.get('raise_exception')
        self.raise_on_second_commit = kwargs.get('raise_on_second_commit')

    def add(self, record):
        self.added_records.append(record)

    def commit(self):
        if self.raise_exception or self.raise_on_second_commit and self.commit_called:
            raise exc.SQLAlchemyError
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

    def query(self, *args):
        self.query_args.append(args)  # Allows params in the select clause of the mocked query to be checked

        if self.mock_query_kwargs:
            return MockQuery(**self.mock_query_kwargs)

        if self.side_effect:
            query_result = self.side_effect[self.query_call_count]  # Expected to be an instance of MockQuery
            self.query_call_count += 1
            return query_result

        return self.return_value


class DummyTmplContext:

    def set_data(self, dct):
        self.__dict__.update(dct)

    def __setattr__(self, key, value):
        self.__dict__[key] = value


class MockRequest(testing.DummyRequest):
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.dbsession = MockDbSession()
        self.registry.settings = {
            'ini_default': config or {},
        }
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
