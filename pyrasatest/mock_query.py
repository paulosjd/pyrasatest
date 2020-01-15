from typing import Iterable, Hashable

from sqlalchemy.sql.elements import Label


class MockQuery:
    filter_args = None

    def __init__(self, all_: Iterable = None,
                 iter_vals: Iterable = None,
                 query_return_values: dict = None,
                 query_select: Hashable = None,
                 raise_exc: [Exception] = None,
                 **kwargs) -> None:
        self.exception_class = raise_exc
        self.all_ = all_ or []
        self.query_return_values = {
            '{}.{}'.format(k, k.key) if isinstance(k, Label) else k: v for k, v
            in query_return_values.items()
        } if query_return_values else {}
        self.query_select = query_select
        # Since hash(Foo.bar.label('abc')) gives unique value
        if isinstance(self.query_select, Label):
            self.query_select = '{}.{}'.format(self.query_select,
                                               self.query_select.key)
        self.first_ = kwargs.get('first_')
        self.one_ = kwargs.get('one_')
        self.scalar_ = kwargs.get('scalar_')
        self.limit_val = kwargs.get('limit_val')
        self.in_return_val = kwargs.get('in_return_val')
        self.count_return_val = kwargs.get('count_return_val')
        self.iter_vals = iter_vals or []
        self.filter_by_kwargs = {}
        self.iter_count = 0
        self.call_count = 0
        # for attr in ['like_args', 'filter_args', 'order_by_args']:
        #     setattr(self, attr, [])

    def __iter__(self):
        if self.iter_vals:
            return iter(self.iter_vals)
        return self

    def __next__(self):
        self.iter_count += 1
        if len(self.all_) >= self.iter_count:
            return self.all_[self.iter_count - 1]
        else:
            self.iter_count = 0
            raise StopIteration

    def first(self):
        if self.query_return_values.get(self.query_select):
            return self.query_return_values[self.query_select]
        return self.first_

    def all(self):
        if self.query_return_values.get(self.query_select):
            return self.query_return_values[self.query_select]
        return self.all_

    def one(self):
        if self.query_return_values.get(self.query_select):
            return self.query_return_values[self.query_select]
        if self.exception_class:
            raise self.exception_class()
        return self.one_

    def scalar(self):
        return self.scalar_

    def count(self):
        return self.count_return_val

    def order_by(self, *args):
        setattr(self, 'order_by_args', args)
        return self

    def filter(self, *args):
        setattr(self, 'filter_args', args)
        return self

    def like(self, *args):
        setattr(self, 'like_args', args)
        return self

    def group_by(self, *args):
        return self

    def join(self, *args):
        return self

    def outerjoin(self, *args):
        return self

    def select_from(self, *args):
        return self

    def correlate(self, *args):
        return self

    def distinct(self, *args):
        return self

    def union(self, *args):
        for mock_q in args:
            self.all_.extend(mock_q.all_)
        return self

    def filter_by(self, **kwargs):
        setattr(self, 'filter_by_kwargs', kwargs)
        return self

    def limit(self, *args):
        return self.limit_val or self

    def subquery(self):
        return self

    def as_scalar(self):
        return self
