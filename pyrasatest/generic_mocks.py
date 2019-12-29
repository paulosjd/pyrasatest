
class MockModel:
    def __init__(self, **kwargs):
        self.save_called = False
        self.delete_called = False
        self.init_kwargs = kwargs
        self._result_items = []
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __len__(self):
        if hasattr(self, 'len_value'):
            return self.len_value
        return len(self.__dict__)

    def to_dict(self, prefix=None, exclude=None):
        dct = {}
        if exclude is None:
            exclude = []
        for k, v in self.__dict__.items():
            if not k.startswith('_') and k not in exclude:
                dct[k] = v if not prefix else prefix + str(v)
        return dct

    def save(self):
        self.save_called = True

    def delete(self):
        self.delete_called = True

    def set_result_items(self, items):
        self._result_items = items

    def __getitem__(self, item):
        if self._result_items:
            return self._result_items[item]
        return list(self.init_kwargs.values())[item]


class LazyAttrMockModel(MockModel):
    def __getattr__(self, item):
        if not self.__dict__.get(item):
            return None
