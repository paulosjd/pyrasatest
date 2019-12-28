**Pyramid SQLAlchemy unit testing utilities**

A package which provides a set of utilities that enables SQLAlchemy functionality to be
mocked in the writing of unit tests for a Pyramid application.

The package was created for situations where it is desirable to mock out the database
layer, such as in cases where its complexity makes test setup overly time-consuming.
It is suited to unit testing applications which use SQLAlchemy as an ORM.

In particular [Pyramid](https://docs.pylonsproject.org/projects/pyramid/en/latest/) applications, 
a framework within which models have no direct awareness of the database and database 
interactions are carried out through `request.dbsession`.

[The source for this project is available here][https://github.com/paulosjd/pyrasatest].


----
**Example usage**

----

**Installation**



