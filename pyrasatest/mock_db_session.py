from sqlalchemy import exc
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .sqlalchemy_mocks import MockQuery


class MockDbSession:
    """
    Usage examples
    --------------
    raise SQLAlchemyError from self.request.dbsession.query(...).one()
        self.view.request.dbsession.mock_query_kwargs = {'raise_exc': SQLAlchemyError}
    """
    def __init__(self, query_return_values=None, **kwargs):
        self.query_return_values = query_return_values or {}
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
        if self.raise_exception or all([self.raise_on_second_commit,
                                        self.commit_called]):
            raise exc.SQLAlchemyError
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

    def query(self, *args):
        self.query_args.append(args)

        if self.side_effect:
            # Expected to be an instance of MockQuery
            query_result = self.side_effect[self.query_call_count]
            self.query_call_count += 1
            return query_result

        if self.return_value:
            return self.return_value

        for key, val in self.query_return_values.items():
            for sa_class, attr in [(DeclarativeMeta, '__table__'),
                                   (InstrumentedAttribute, 'property')]:
                if isinstance(key, sa_class):
                    attr_eq = getattr(key, attr) == getattr(args[0], attr, '')
                    try:
                        if attr_eq and issubclass(val, Exception):
                            raise val
                    except TypeError:
                        pass

        return MockQuery(query_select=args[0],
                         query_return_values=self.query_return_values)
