import unittest

from pyrasatest.mock_model import LazyAttrMockModel, MockModel


class MockModelTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_model = MockModel()

    def test_len_method_with_len_value_attr_set(self):
        mm = MockModel(len_value=5)
        self.assertEqual(5, len(mm))

    def test_len_method_without_len_value_attr_set(self):
        self.assertEqual(len(self.mock_model.__dict__),
                         len(self.mock_model))

    def test_to_dict_method_exclude_is_none(self):
        dct = {'foo': 'bar', 'eggs': 'ham'}
        mm = MockModel(**dct)
        self.assertEqual(dct, mm.to_dict())

    def test_to_dict_method_exclude_is_not_none(self):
        dct = {'foo': 'bar', 'eggs': 'ham'}
        mm = MockModel(**dct)
        self.assertEqual({'eggs': 'ham'}, mm.to_dict(exclude=['foo']))

    def test_save_and_delete_methods(self):
        for mtd in ['save', 'delete']:
            getattr(self.mock_model, mtd)()
            self.assertTrue(getattr(self.mock_model, f'{mtd}_called'))

    def test_set_result_items(self):
        self.mock_model.set_result_items(['foo', 'bar'])
        self.assertEqual(['foo', 'bar'], self.mock_model._result_items)

    def test_getitem_with_result_items_set(self):
        self.mock_model._result_items = ['foo', 'bar']
        self.assertEqual('foo', self.mock_model[0])

    def test_getitem_with_object_uses_init_kwargs(self):
        mock_model = MockModel(foo=1, bar=2)
        self.assertEqual(2, mock_model[1])

    def test_lazy_attr_mock_model_not_raises_attribute_error(self):
        self.assertIsNone(LazyAttrMockModel().attr_not_exist)
