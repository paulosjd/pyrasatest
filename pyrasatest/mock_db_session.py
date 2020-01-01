from sqlalchemy import exc
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .mock_query import MockQuery


class MockDbSession:
    # TODO Typing e.g. query_return_values optional, dict
    def __init__(self, query_return_values=None, **kwargs):
        self.query_return_values = query_return_values or {}
        self.return_value = None
        self.side_effect = None
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

        if self.query_return_values:
            self.check_for_raise_condition(args[0])

        if self.side_effect:
            # Expected to be an instance of MockQuery
            query_result = self.side_effect[self.query_call_count]
            self.query_call_count += 1
            return query_result

        if self.return_value:
            return self.return_value

        return MockQuery(query_select=args[0],
                         query_return_values=self.query_return_values)

    def check_for_raise_condition(self, first_arg):
        """ Check 'query_return_values' whether Exception should be raised """
        for key, val in self.query_return_values.items():
            for sa_class, attr in [(DeclarativeMeta, '__table__'),
                                   (InstrumentedAttribute, 'property')]:
                if isinstance(key, sa_class):
                    attr_eq = getattr(key, attr) == getattr(first_arg, attr, '')
                    try:
                        if attr_eq and issubclass(val, Exception):
                            raise val
                    except TypeError:
                        pass


class PartialMockDbSession(MockDbSession):
    def __init__(self, query_return_values=None, dbsession=None, **kwargs):
        """ Creates an instance for intended use of ...
        :param dbsession: instance of sqlalchemy.orm.Session
        :param query_return_values: dict where each key is a model or model
        property. If it is the first positional argument passed to a
        dbession.query call, then the query will be mocked and the value will
        be used as the return value from any chained .one(), .first() or .all()
        calls, or an Exception raised if the value is an Exception class.
        values from the mocked queries.
        :return: MockDbSession instance
        """
        assert query_return_values, 'query_return_values truthiness test failed'
        assert dbsession, 'dbsession truthiness test failed'
        super().__init__(query_return_values=query_return_values, **kwargs)
        self.dbsession = dbsession

    def query(self, *args):

        if args[0] not in self.query_return_values:
            return self.dbsession.query(*args)

        return super().query(*args)
