import unittest

from pyrasatest.mock_query import MockQuery


class MockQueryTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_query = MockQuery()

    def test_iter_method_with_has_iter_vals_attr_returns_iterator(self):
        mock_query = MockQuery(iter_vals=[1, 2])
        iterator = iter(mock_query)
        self.assertTrue(hasattr(iterator, '__next__'))
        self.assertEqual([1, 2], list(iterator))

    def test_iter_method_not_has_iter_vals_attr_returns_self(self):
        self.assertEqual(self.mock_query, iter(self.mock_query))

    def test_next_method_with_len_of_all_ge_iter_count(self):
        mock_query = MockQuery(all_=[1])
        self.assertEqual(mock_query.all_[self.mock_query.iter_count - 1],
                         next(mock_query))
        self.assertEqual(1, mock_query.iter_count)

    def test_next_method_with_len_of_all_not_ge_iter_count(self):
        self.mock_query.iter_count += 1
        with self.assertRaises(StopIteration):
            next(self.mock_query)
        self.assertEqual(0, self.mock_query.iter_count)

    def test_first_and_all_and_one_methods_with_attr_dot_get_truthy(self):
        self.mock_query.query_return_values = {'foo': 'bar'}
        self.mock_query.query_select = 'foo'
        for mtd in ['first', 'all', 'one']:
            self.assertEqual('bar', getattr(self.mock_query, mtd)())

    def test_first_and_all_and_one_and_scalar_methods_with_default(self):
        for mtd in ['first', 'all', 'one', 'scalar']:
            setattr(self.mock_query, f'{mtd}_', f'{mtd}_val')
            self.assertEqual(f'{mtd}_val', getattr(self.mock_query, mtd)())

    def test_one_with_raise_exc_condition(self):
        self.mock_query.exception_class = KeyError
        with self.assertRaises(KeyError):
            self.mock_query.one()

    def test_order_by_and_filter_and_like_methods(self):
        arg = 'abc'
        for mtd in ['order_by', 'filter', 'like']:
            self.assertEqual(self.mock_query,
                             getattr(self.mock_query, mtd)(arg))
            self.assertEqual((arg, ),
                             getattr(self.mock_query, f'{mtd}_args'))

    def test_group_by_and_join_and_outerjoin_and_select_from_methods(self):
        for mtd in ['group_by', 'join', 'outerjoin', 'select_from',
                    'correlate', 'distinct', 'limit']:
            self.assertEqual(self.mock_query,
                             getattr(self.mock_query, mtd)('foo'))

    def test_count_method(self):
        self.mock_query.count_return_val = 5
        self.assertEqual(5, self.mock_query.count())

    def test_union_method(self):
        mock_query_1 = MockQuery(all_=[1, 2])
        self.assertEqual(mock_query_1,
                         mock_query_1.union(MockQuery(all_=[3, 4])))
        self.assertEqual([1, 2] + [3, 4], mock_query_1.all_)

    def test_filter_by_method(self):
        self.mock_query.filter_by(foo='bar')
        self.assertEqual(self.mock_query, self.mock_query.filter_by(foo='bar'))
        self.assertEqual({'foo': 'bar'}, self.mock_query.filter_by_kwargs)

    def test_subquery_and_as_scalar_methods(self):
        for mtd in ['subquery', 'as_scalar']:
            self.assertEqual(self.mock_query, getattr(self.mock_query, mtd)())
