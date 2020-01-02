**Pyramid SQLAlchemy unit testing utilities**

A package which provides Python classes that enables SQLAlchemy functionality to be
mocked in unit tests for an application written in Pyramid or a similar framework.

These utilities are designed to help in writing unit tests for situations 
where test setup is overly time-consuming or otherwise problematic. 
This may include the requirement for extensive amounts of request data for which
queries filter upon, or for an extensive variety of related records
to be created due to complex database schemas etc.

In mocking and explicitly setting return
values for SQLAlchemy queries, the appreciation of
control flow is made easier in many cases. Note that in using the provided objects,
such as mocking SQLAlchemy ORM queries through `MockDbSession`,
whether queries are written correctly or return results are as expected
is left untested. 

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

For testing code which accesses an SQLAlchemy query result object using indexing
as an alternative to dotted attribute lookup (i.e. `namedtuple`-like access),
values will be returned according to ordering of kwargs which are passed to the constructor, for example:

    >>> mock_model = MockModel(foo='0', bar='1')
    >>> mock_model[0]
    '0'
    
For Python versions before 3.6, where dictionaries have no ordering, the following
method should be used to specify return values from indexing:
    
    >>> mock_model.set_result_items(['foo_value', 'bar_value'])
    >>> mock_model[0]
    'foo_value'

`LazyAttrMockModel` is similar to `MockModel` except that in the case of a 
failed attribute lookup, it will return `None` instead of raising `AttributeError`.

**`MockRequest`**

`MockRequest` objects, which inherit from `Pyramid.testing.DummyRequest`,
have an instance of `MockDbSession` as an attribute. 
Database interactions, which would usually involve an SQLAlchemy session instance
through `request.dbsession`, will use an instance of `MockDbSession` instead. 
This can be customized accordingly, usage is demonstrated below.

**`MockDbSession`**

To set query results more generally, see `MockQuery` usage notes.
Query results can be set in a specific manner,
according to the model or model property which 
is the first positional argument passed to `dbession.query` in the unit of code
being tested. The following view callable has multiple `dbession.query` calls:

    class ExampleView:
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

    ...
    from pyrasatest import MockModel, MockRequest
    from sqlalchemy import exc
    
    from app.models import Account, Order, Product
    from app.views.default import ExampleView

    class ExampleViewTestCase(unittest.TestCase):
        def setUp(self):
            self.view = ExampleView(MockRequest())
    
        def test_get_order_info_order_not_found(self):
            self.view.request.dbsession.query_return_values = {
                Order: exc.SQLAlchemyError
            }
            self.assertEqual(
                {'status': 'order not found'},
                self.view.get_order_info()
            )
    
        def test_get_order_info_product_not_found(self):
            mock_order = MockModel(id=12)
            self.view.request.dbsession.query_return_values = {
                # MockQuery can be used as a value, this allows customization
                # Order: MockQuery(one_=mock_order) 
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

**`PartialMockDbSession`**

Subclasses `MockDbSession` and makes it so ORM query mocking is restricted to 
only the specified queries. In creating an instance,
a test database session instance must be provided,
as well as a `dict` whose data specifies which queries 
to mock along with desired return values.

If a `dbsession.query` call contains no key matching the first positional 
argument passed to it, then that call will not be mocked. 
Otherwise it is used as the return value from any 
chained `.one()`, `.first()` or `.all()` calls,
or an `Exception` raised if the value is an `Exception` class. 

In the following example, suppose a unit of code being tested contained the
following `dbsession.query` calls:

    accounts = request.dbsession.query(Account).filter(...).one()
    supplier = request.dbsession.query(Supplier, Country.id).filter(...).one()
    products = request.dbsession.query(Product.id).filter(...).all()

Then to selectively mock the last two calls (and leave the first one unmocked), 
`PartialMockDbSession` can be used as follows:

    ...
    from pyramid.testing import DummyRequest
    from pyrasatest import PartialMockDbSession
    from sqlalchemy import exc
    
    from app.models import Account, Supplier, Product
    from app.models.meta import Base
    from app.views import ExampleView

    class ExampleViewTestCase(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            engine = create_engine('sqlite:///:memory:')
            cls.session = scoped_session(sessionmaker(bind=engine))
            Base.metadata.create_all(engine)
            request = DummyRequest()
            request.dbsession = cls.session
            cls.view = ExampleView(request)
            acc1 = Account(name='acc1', number='123')
            ...


        def test_get_account_and_product_number_with_mocked_product_query(self):
            self.view.request.params = {'account_id': self.accounts[0].id}
            mock_product = MockModel(number=32)
            self.view.request.dbsession = PartialMockDbSession(
                query_return_values={Product.id: mock_product},
                dbsession=self.session
            )
            acc_name = self.accounts[0].name
            self.assertEqual(
                {'account_name': acc_name, 'product_number': mock_product[0]},
                self.view.get_account_and_product_number()
            )

**`MockQuery`**

As defined in `MockQuery.__init__`, a number of keywords arguments have meaning
which affect behavior on subsequent method calls.

To set returns values for queries which end in `.first()` and `.one()` as in the
following view callable:

    class ExampleView:
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
    
    from app.views.default import ExampleView

    class ExampleViewTestCase(unittest.TestCase):
        def setUp(self):
            self.view = ExampleView(MockRequest()) 

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
over the result, pass in the desired return value in a manner similar to:  
`MockQuery(all_=['result1', 'result2'])`

----

**Installation**

To install the package you can use pip:

    $ pip install pyrasatest