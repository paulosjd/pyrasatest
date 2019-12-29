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
**Available functionality and example usage**

**`class MockModel`** is useful for representing ORM objects, whereby desired attributes
are set in their construction from keywords arguments.

As defined in `MockModel.__init__`, a number of keywords arguments have meaning
beyond being used to set attributes and are useful in specifying desired behaviour:

    >>> from pyrasatest import MockModel
    >>> mm = MockModel(name='Paul', age='34')
    >>> print(f'My name is {mm.name} and my age is {mm.age}')
    My name is Paul and my age is 34

**`class LazyAttrMockModel`** is similar to `MockModel` except that in the case of a 
failed attribute lookup, it will return `None` instead of raising `AttributeError`.

**`class MockDbSession`**

For testing code which access an SQLAlchemy object `Result` which uses indexing
as alternative to dotted attribute lookup (i.e. allow `namedtuple`-like interface),
values will be returned according to ordering of kwargs which are passed to the constructor, for example:

    mock_model = MockModel(foo='0', bar='1')
    mock_model[0]
    '0'
    
For Python versions before 3.6, where dictionaries have no ordering, the following
method should be used to specify return values from indexing:
    
    mock_model.set_result_items(['foo_value', 'bar_value'])
    mock_model[0]
    'foo_value'

To set query results more generally, use:

Query results can be specified according to the model or model property which 
is the first positional argument passed to `dbession.query`.
The following view callable has multiple `dbession.query` calls:

    class OrderInfoView:
        def __init__(self, request):
            self.request = request
    
        @view_config(route_name='order_info', renderer='../templates/mytemplate.mako')
        def get_order_info(self):
            try:
                order = self.request.dbsession.query(models.Order).filter(
                    models.Order.id == self.request.params.get('order_id')).one()
                a = type(order)
            except exc.SQLAlchemyError:
                return {'status': 'order not found'}
    
            try:
                product_id = self.request.dbsession.query(models.Product.id).filter(
                    models.Product.number == self.request.params.get('product_number')).one()[0]
            except exc.SQLAlchemyError:
                return {'status': f'product not found for order id {order.id}'}
    
            try:
                acc_name = self.request.dbsession.query(models.Account.name).filter(
                    models.Account.id == self.request.params.get('account_id')).one()[0]
            except exc.SQLAlchemyError:
                return {'status': f'account not found for order id {order.id}'}
    
            return {
                'status': 'ok',
                'order_number': order.number,
                'product_id': product_id,
                'account_name': acc_name,
            }
    
The following tests for the above demonstrates the setting of return values 
for specific queries:

    import unittest
    
    from pyrasatest import MockModel, MockRequest
    from sqlalchemy import exc
    
    from ..models import Account, Order, Product
    from ..views.default import OrderInfoView
    

    class OrderInfoViewTestCase(unittest.TestCase):
        def setUp(self):
            self.view = OrderInfoView(MockRequest())
    
        def test_get_order_info_order_not_found(self):
            self.view.request.dbsession.query_return_values = {Order: exc.SQLAlchemyError}
            self.assertEqual(
                {'status': 'order not found'},
                self.view.get_order_info()
            )
    
        def test_get_order_info_product_not_found(self):
            mock_order = MockModel(id=12)
            self.view.request.dbsession.query_return_values = {
                Order: mock_order,
                Product.id: exc.SQLAlchemyError
            }
            self.assertEqual(
                {'status': f'product not found for order id {mock_order.id}'},
                self.view.get_order_info()
            )
    
        def test_get_order_info_account_not_found(self):
            mock_order = MockModel(id=12)
            self.view.request.dbsession.query_return_values = {
                Order: mock_order,
                Product.id: MockModel(id=25),
                Account.name: exc.SQLAlchemyError
            }
            self.assertEqual(
                {'status': f'account not found for order id {mock_order.id}'},
                self.view.get_order_info()
            )
    
        def test_get_order_info(self):
            mock_order = MockModel(id=12, number=5)
            mock_product = MockModel(id=25)
            mock_account = MockModel(name='test_acc')
            query_return_values = {
                Order: mock_order,
                Product.id: mock_product,
                Account.name: mock_account
            }
            self.view.request.dbsession.query_return_values = query_return_values
            expected_output = {
                'status': 'ok',
                'order_number': mock_order.number,
                'product_id': mock_product[0],
                'account_name': mock_account[0],
            }
            self.assertEqual(expected_output, self.view.get_order_info())
