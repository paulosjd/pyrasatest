import unittest
from collections import namedtuple
from unittest.mock import patch

from sqlalchemy import Column, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import as_declarative

from pyrasatest.mock_db_session import MockDbSession, PartialMockDbSession
from pyrasatest.mock_query import MockQuery


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True)


class TestModel(Base):
    __tablename__ = 'test'
    number = Column(Integer)


class MockDbSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_db_session = MockDbSession()
        self.query_args = ['1', '2']

    def test_add_method(self):
        self.mock_db_session.add('record')
        self.assertIn('record', self.mock_db_session.added_records)

    def test_commit_raises_when_set(self):
        mock_db_session = MockDbSession(raise_exception=True)
        with self.assertRaises(SQLAlchemyError):
            mock_db_session.commit()

    def test_commit_success_set(self):
        self.mock_db_session.commit()
        self.assertTrue(self.mock_db_session.commit_called)

    def test_rollback_success_set(self):
        self.mock_db_session.rollback()
        self.assertTrue(self.mock_db_session.rollback_called)

    def test_query_with_query_return_values_attr_having_mock_query_value(self):
        mock_query = MockQuery()
        mock_db_session = MockDbSession(
            query_return_values={self.query_args[0]: mock_query}
        )
        self.assertEqual(mock_query, mock_db_session.query(*self.query_args))

    @patch('pyrasatest.mock_db_session.MockDbSession.check_for_raise_condition')
    def test_query_with_query_return_values_attr_returns_mock_query(
            self, check_raise_condition_patch):
        qrv = {self.query_args[0]: 'foo'}
        mock_db_session = MockDbSession(query_return_values=qrv)
        rtn_val = mock_db_session.query(*self.query_args)
        self.assertIsInstance(rtn_val, MockQuery)
        check_raise_condition_patch.assert_called_with(self.query_args[0])
        self.assertEqual(self.query_args[0], getattr(rtn_val, 'query_select'))
        self.assertEqual(qrv, getattr(rtn_val, 'query_return_values'))

    def test_query_with_side_effect_attr_truthy(self):
        self.mock_db_session.side_effect = ['a', 'b']
        self.assertEqual('a', self.mock_db_session.query(*self.query_args))
        self.assertEqual('b', self.mock_db_session.query(*self.query_args))

    def test_query_with_return_value_attr_truthy(self):
        self.mock_db_session.return_value = 'foo'
        self.assertEqual('foo', self.mock_db_session.query(*self.query_args))

    def test_check_for_raise_condition_table_references_exception(self):
        self.mock_db_session.query_return_values = {
            'a': 1,
            TestModel: ValueError
        }
        with self.assertRaises(ValueError):
            self.mock_db_session.check_for_raise_condition(TestModel)

    def test_check_for_raise_condition_property_references_non_exception(self):
        self.mock_db_session.query_return_values = {TestModel.number: 5}
        self.assertIsNone(
            self.mock_db_session.check_for_raise_condition(TestModel.number)
        )

    def test_partial_mock_db_session_returns_unmock_query_call(self):
        mock_scoped_session = namedtuple('mock_scoped_session',
                                         'query')(lambda x: 'ss_called')
        instance = PartialMockDbSession(query_return_values={'y': 1},
                                        dbsession=mock_scoped_session)
        self.assertEqual(mock_scoped_session.query('x'),
                         instance.query('x'))

    def test_partial_mock_db_session_returns_mock_query_call(self):
        instance = PartialMockDbSession(query_return_values={'y': 1},
                                        dbsession='no query attribute')
        self.assertEqual(type(self.mock_db_session.query('y')),
                         type(instance.query('y')))
