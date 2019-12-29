**Pyramid SQLAlchemy unit testing utilities**

A package which provides a set of utilities that enables SQLAlchemy functionality to be
mocked in unit tests for an application written in Pyramid or a similar framework.

In mocking interactions with the database layer, 
time and effort expenditure associated with test setup can
be reduced. By setting explicit return values for ORM queries, 
control flow is simplified, both in the writing tests and the reading 
of tests.

Little functionality is provided to facilitate testing 
whether usage of APIs such as SQLAlchemy ORM queries is correct or behaves as expected.
However, through a configuration file, tests that mock such interactions using
a `patch` decorator can be selectively `unpatched`.

It is suited to unit testing applications which use SQLAlchemy as an ORM,
and a framework such as [Pyramid](https://docs.pylonsproject.org/projects/pyramid/en/latest/), 
within which models have no direct awareness of the database. For Pyramid,
where database interactions are carried out through `request.dbsession`,
the replacement mock database session functionality is provided accordingly.
`MockDbSession` is still otherwise available to import and use in the creation
of test objects.

[The source for this project is available here][https://github.com/paulosjd/pyrasatest].


----
**Example usage**

    class BaseViewsTestCase(unittest.TestCase)
    
        def setUp(self):
            super().setUp()
            self.view.c = DummyTmplContext()
            self.view.request = MockRequest()  # Pyramid object which inherits from dict
            self.view.session = MockSession()  # Pyramid object which inherits from dict
            self.view.session['user_account_id'] = getattr(self, 'user_account_id', self.default_user_account_id)
            self.view.jsonFlashMessage = self.mock_json_flash_message
            self.view.render = lambda x: self.render_rtn_val
            self.model_save_call_count = 0
            self.model_sync_call_count = 0
            # With patch and replace with self.mock_model_sync that my_model.sync({'foo': 'bar'}) --> [[{'foo': 'bar'}, ], ]
            self.model_sync_call_args = []
            # To allow successive MockQuery objects to be returned upon successive 'view.dbsession' calls
            self.mock_db_queries = [
                MockQuery()]  # Should generally be set at the beginning of each test where necessary
            self.db_query_index = 0
