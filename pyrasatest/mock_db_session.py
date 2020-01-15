from sqlalchemy import exc
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import Label

from .mock_query import MockQuery


class MockDbSession:
    def __init__(self, query_return_values: dict = None, **kwargs) -> None:
        self.query_return_values = query_return_values or {}
        for k in self.query_return_values.keys():
            if isinstance(k, Label):
                self.query_return_values.update({
                    str(k): self.query_return_values.pop(k)
                })
        self.raise_exception = kwargs.get('raise_exception')
        self.return_value = None
        self.side_effect = None
        self.commit_called = False
        self.rollback_called = False
        self.query_call_count = 0
        self.added_records = []

    def add(self, record):
        self.added_records.append(record)

    def commit(self):
        if self.raise_exception:
            raise exc.SQLAlchemyError
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

    def query(self, *args):
        first_param = str(args[0]) if isinstance(args[0], Label) else args[0]

        if self.query_return_values:
            if isinstance(self.query_return_values.get(first_param), MockQuery):
                return self.query_return_values[first_param]
            self.check_for_raise_condition(first_param)

        if self.side_effect:
            # Expected to be an instance of MockQuery
            query_result = self.side_effect[self.query_call_count]
            self.query_call_count += 1
            return query_result

        if self.return_value:
            return self.return_value

        return MockQuery(query_select=first_param,
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
        """ Similar to MockDbSession but uses SQLAlchemy ORM queries
         (i.e. not mocked) if these first positional argument passed to the
         'query' method does not match any keys in 'query_return_values'
        :param dbsession: instance of sqlalchemy.orm.Session
        :param query_return_values: dict where each key is a model or model
        property. If it is the first positional argument passed to a
        dbession.query call, then the query will be mocked and the value will
        be used as the return value from any chained .one(), .first() or .all()
        calls, or an Exception raised if the value is an Exception class.
        :return: MockDbSession instance
        """
        assert query_return_values, 'query_return_values truthiness test failed'
        assert dbsession, 'dbsession truthiness test failed'
        super().__init__(query_return_values=query_return_values, **kwargs)
        self.dbsession = dbsession

    def query(self, *args):
        first_param = str(args[0]) if isinstance(args[0], Label) else args[0]

        if first_param not in self.query_return_values:
            return self.dbsession.query(*args)

        return super().query(*args)
