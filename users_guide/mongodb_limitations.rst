.. _mongodb_limitations:

Limitations of the MongoDB OML
==============================

Although MongoDB OML is very flexible and powerful, it is not perfect. In this
section we'll enumerate a number of issues that you should be aware of when
deciding whether or not to use MongoDB OML for your application.

Facets Issues
-------------

* In order to achieve the correct *deferred* semantics for *DBLink(s)* and
  *DBRef(s)* facets, the code that loads an existing object from a MongoDB
  database does not trigger a facet change notification when initializing any
  *deferred* mode facet. This is because a Facets change notification includes
  the new value of a facet as part of its information payload. Since the whole
  point of using a *deferred* mode facet is to delay loading the actual value of
  the facet until your application code actually uses it, generating the change
  notification would nullify the advantage of this MongoDB OML facet feature.
  
  Note that it is possible that a planned architectural change to the Facets
  package may resolve this problem in the future, at which time this item will
  be removed.
  
MongoDB OML Issues
------------------

* The MongoDB OML is a software layer built on top of MongoDB that provides a
  Facets-based object oriented persistent storage model. MongoDB is a
  document-centric, No SQL database. Although the two fit well together, they
  are not the same thing. 
  
  There are many features of MongoDB that are not exposed or used by the MongoDB
  OML. As such, there may be cases where direct use of the MongoDB feature set
  may be more appropriate for your application design. If there are features
  that MongoDB OML does not provide, you might want to look at the MongoDB
  documentation to see if using the MongoDB API directly might be a better fit
  for your application.
  
MongoDB Issues
--------------

* Perhaps the biggest potential issue with basing an application on MongoDB is
  its lack of atomic multi-document updates or transactions. That is, MongoDB
  does not provide a mechanism for making any change that affects more than a 
  single document appear as a single, consistent database update. 
  
  Although all changes made on a single database connection are made 
  sequentially, there is the possibility that in an environment supporting
  multiple, simultaneous connections, updates made by different connections may
  get inter-mingled. If the changes happen to affect the same set of documents,
  the final result may not be self-consistent.
  
  In terms of MongoDB OML, there is a one-to-one mapping between your
  application objects and MongoDB *documents*. Therefore, if your application
  changes multiple objects and then saves them, there is no guarantee that some
  other application may not be updating the same database objects at the same
  time. If that situation occurs, it is possible that the final MongoDB database
  state may reflect some, but not all, of the changes made by each client
  application, potentially leaving the database in an inconsistent state.
  
  Currently this is a problem that has to be dealt with at the application
  level. There may be some additional enhancements made to the MongoDB OML
  package in the future that help with this issue. It is also possible that
  MongoDB may itself add some enhancements in this area as well, although the
  author is not aware of any planned work in this area at the moment.

