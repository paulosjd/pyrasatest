import unittest

from pyrasatest.mock_db_session import MockDbSession
from pyrasatest.mock_pyramid_objects import (
    DummyTmplContext, MockRequest, MockSession
)


class MockPyramidObjectsTestCase(unittest.TestCase):

    def test_dummy_tmpl_context_set_data(self):
        dtc = DummyTmplContext()
        dtc.set_data({'foo': 'bar'})
        self.assertEqual('bar', getattr(dtc, 'foo'))

    def test_mock_request_init_method(self):
        mock_req = MockRequest()
        self.assertIsInstance(mock_req.dbsession, MockDbSession)
        self.assertIsInstance(mock_req.tmpl_context, DummyTmplContext)

    def test_mock_request_methods(self):
        mock_req = MockRequest()
        for mtd in ['route_url', 'static_url', 'route_path']:
            self.assertEqual(getattr(mock_req, f'mock_{mtd}'),
                             getattr(mock_req, mtd)('', foo='bar'))

    def test_mock_session_save_method(self):
        session = MockSession()
        session.save()
        self.assertTrue(session.save_called)
