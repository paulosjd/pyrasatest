
class MockQuery:
    filter_args = None

    def __init__(self, raise_exc=None, **kwargs):
        self.exception_class = raise_exc
        self.count_return_val = kwargs.get('count_val', None)
        self.query_select = kwargs.get('query_select', None)
        self.query_return_values = kwargs.get('query_return_values', {})
        self.all_ = kwargs.get('all_', [])
        self.iter_vals = kwargs.get('iter_vals', [])
        self.first_successive_return_vals = kwargs.get(
            'first_successive_return_vals', [])
        self.all_successive_return_vals = kwargs.get(
            'all_successive_return_vals', [])
        self.filter_by_kwargs = {}
        self.iter_count = 0
        self.call_count = 0
        for attr in ['first_', 'one_', 'in_return_val', 'get_', 'limit_val',
                     'scalar_']:
            return_val = kwargs.get(attr, kwargs.get(attr.strip('_'), None))
            setattr(self, attr, return_val)
        for attr in ['like_args', 'ordered_by', 'filter_args',
                     'with_hint_args']:
            setattr(self, attr, [])

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
        if self.first_successive_return_vals:
            return self.first_successive_return_vals.pop(0)
        return self.first_

    def order_by(self, *args):
        self.ordered_by.append(args)
        return self

    def all(self):
        if self.query_return_values.get(self.query_select):
            return self.query_return_values[self.query_select]
        if self.all_successive_return_vals:
            return self.all_successive_return_vals.pop(0)
        return self.all_

    def one(self):
        if self.query_return_values.get(self.query_select):
            return self.query_return_values[self.query_select]
        if self.exception_class:
            raise self.exception_class()
        return self.one_

    def in_(self, iterable):
        return self.in_return_val

    def subquery(self):
        return self

    def group_by(self, *args):
        return self

    def join(self, *args):
        return self

    def outerjoin(self, *args):
        return self

    def union(self, *args):
        for mock_q in args:
            self.all_.extend(mock_q.all_)
        return self

    def select_from(self, *args):
        return self

    def limit(self, *args):
        return self.limit_val or self

    def correlate(self, *args):
        return self

    def as_scalar(self):
        return self

    def distinct(self, *args):
        return self

    def like(self, *args):
        self.like_args.append(args)
        return self

    def filter(self, *args):
        self.filter_args.append(args[0])
        return self

    def filter_by(self, **kwargs):
        self.filter_by_kwargs.update(kwargs)
        return self

    def count(self):
        return self.count_return_val

    def scalar(self):
        return self.scalar_