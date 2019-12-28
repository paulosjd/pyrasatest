
class MockModel:
    def __init__(self, **kwargs):
        self.save_called = False
        self.delete_called = False
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __len__(self):
        if hasattr(self, 'len_value'):
            return self.len_value
        return len(self.__dict__)

    def to_dict(self, prefix=None, exclude=None):
        _dict = {}
        if exclude is None:
            exclude = []
        for k, v in self.__dict__.items():
            if not k.startswith('_') and k not in exclude:
                _dict[k] = v if not prefix else prefix + str(v)
        return _dict

    def save(self):
        self.save_called = True

    def delete(self):
        self.delete_called = True


class LazyAttrMockModel(MockModel):
    def __getattr__(self, item):
        if not self.__dict__.get(item):
            return None


def mock_callable(*args, **kwargs):
    return 'mock_callable called'


class MockCsvWriter:
    def __init__(self):
        self.written = []

    def writerow(self, row):
        self.written.append(row)


class MockOpen:
    def __init__(self, *args):
        pass

    def __enter__(self):
        raise FileNotFoundError

    def __exit__(self, *args):
        pass


class MockOpenFileNotFound(MockOpen):
    def __enter__(self):
        raise FileNotFoundError
