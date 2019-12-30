**Pyramid SQLAlchemy unit testing utilities**

A package which provides a set of utilities that enables SQLAlchemy functionality to be
mocked in unit tests for an application written in Pyramid or a similar framework.

In mocking interactions with the database layer, 
time and effort expenditure associated with test setup can
be reduced. By setting explicit return values for ORM queries, 
control flow is simplified, both in the writing tests and reading 
them. It can also save time in writing tests by avoiding the need to 
setup params used in such queries, such as in cases of filtering on request
parameters.

Note that in using the provided objects, for instance in mocking
SQLAlchemy ORM queries through `MockDbSession`,
whether queries are written correctly or return results are as expected
is left untested.

The package written to assist unit testing of applications which use
SQLAlchemy as a database backend,
and a framework such as [Pyramid](https://docs.pylonsproject.org/projects/pyramid/en/latest/), 
in which models have no direct awareness of the database. For Pyramid,
where database interactions made within view callables are 
carried out through `request.dbsession`, a mock database session is provided accordingly.
`MockDbSession` is still otherwise available to import and use in the creation
of test objects.

The source for this project is available [here](https://github.com/paulosjd/pyrasatest).

----
**Available functionality and example usage**

**`MockModel`** 

Useful for representing objects such as ORM query results. 
Desired attributes are set in their construction from keywords arguments.

    >>> from pyrasatest import MockModel
    >>> mm = MockModel(name='Paul', age='34')
    >>> print(f'My name is {mm.name} and my age is {mm.age}')
    My name is Paul and my age is 34

`LazyAttrMockModel` is similar to `MockModel` except that in the case of a 
failed attribute lookup, it will return `None` instead of raising `AttributeError`.

**`MockRequest`**

`MockRequest` objects, which inherit from `Pyramid.testing.DummyRequest`,
have an instance of `MockDbSession` as an attribute. 
In passing a `MockRequest` instance to a Pyramid view callable, database 
interactions which would
usually involve an SQLAlchemy session instance through `request.dbsession` will instead
use `MockDbSession`. Usage is demonstrated in examples below.

**`MockDbSession`**

For testing code which accesses an SQLAlchemy object `Result` which uses indexing
as alternative to dotted attribute lookup (i.e. `namedtuple`-like access),
values will be returned according to ordering of kwargs which are passed to the constructor, for example:

    >>> mock_model = MockModel(foo='0', bar='1')
    >>> mock_model[0]
    '0'
    
For Python versions before 3.6, where dictionaries have no ordering, the following
method should be used to specify return values from indexing:
    
    >>> mock_model.set_result_items(['foo_value', 'bar_value'])
    >>> mock_model[0]
    'foo_value'

To set query results more generally, use `MockQuery` as described below.
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

**`MockQuery`**

As defined in `MockQuery.__init__`, a number of keywords arguments have meaning
which affect behavior on subsequent method calls.

To set returns values for queries which end in `.first()` and `.one()` as in the
following view callable:

    class OrderInfoView:
        def __init__(self, request):
            self.request = request
    
        @view_config(route_name='account_info', renderer=template_path)
        def get_account_info(self):
            account = self.request.dbsession.query(models.Account).filter(
                models.Account.id == self.request.params.get('account_id')
            ).first()
            if not account:
                try:
                    account = self.request.dbsession.query(models.Account).filter(
                        models.Account.name == 'guest'
                    ).one()
                except exc.SQLAlchemyError:
                    return {}
            return {'account_name': account.name, 'account_number': account.number}

Instantiate `MockQuery` with the appropriate keyword arguments and assign to `self.request.dbsession`
as in the following example. Usage also involves testing of a condition where 
`exc.SQLAlchemy` is raised:

    from pyrasatest import MockModel, MockQuery
    from sqlalchemy import exc
    
    from ..views.default import AccountInfoView


    class AccountInfoViewTestCase(unittest.TestCase):
        def setUp(self):
            self.view = AccountInfoView(MockRequest()) 

        def test_get_account_info(self):
            mock_acc = MockModel(name='Abc', number='123')
            self.view.request.dbsession.return_value = MockQuery(first_=mock_acc)
            self.assertEqual(
                {'account_name': mock_acc.name, 'account_number': mock_acc.number},
                self.view.get_account_info()
            )
    
        def test_get_account_info_account_not_found(self):
            self.view.request.dbsession.return_value = MockQuery(
                first_=None,
                raise_exc=exc.SQLAlchemyError
            )
            self.assertEqual({}, self.view.get_account_info())

For query results returned by `.all()`, where the code being tested iterates 
over the result, pass in the desired return value in a manner similar to 
`MockQuery(all_=['result1', 'result2'])`.

----
**Installation**

To install the package you can use pip:

    $ pip install pyrasatest