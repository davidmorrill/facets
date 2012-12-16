.. _mongodb_mongodbobject:

The MongoDBObject Class
=======================

As stated previously, in order for an object to be successfully stored in a
MongoDB database, its class must be a subclass of MongoDBObject, which can be
imported from *facets.extra.mongodb.api*. Deriving from MongoDBObject has three
main functions:

* It provides you with several important methods used for database access
  (*save*, *delete*, *load*, *all*, *iterall*, *fetch*)
* It provides the context that the *DBxxx* facets need to operate correctly.
* It provides all of the Facets metadata and event processing needed to make the
  MongoDB OML *plumbing* work correctly under the covers.

For the most part, you can ignore the details of the last item and only focus
your attention on the first two. We'll cover the use of the various MongoDB
*DBxxx* facets in the next section and continue on here by describing the
various MongoDB database access methods:

**save()**
    Immediately saves the object to its corresponding MondoDB database
    collection. The only time that an object must *explicitly* be saved to a
    MongoDB database is in the case of a new top-level database object.

    A *top-level* object is an object not currently referenced by any other
    object in the database. Such objects are typically retrieved later using one
    of the available query methods.

    In other cases, objects are *implicitly* saved when the application
    terminates or the MongoDB class's *save* method is called. Of course, using
    these facilities can introduce database update delays, so you may still
    want to use explicit *save* calls to exercise more control over the current
    state of the MongoDB database.

    Note that explicitly saving an object may also cause other objects related
    to the object being saved to also be saved at the same time. Examples of
    this would be newly created objects assigned to *DBRef*, *DBRefs*, *DBLink*
    or *DBLinks* facets that are part of the object being saved. The MongoDB OML
    layer detects that such objects are not currently in the database and
    automatically adds them to the database in order to make sure the original
    object has valid database state information about the objects it references.

    The *save* method can be applied to new objects not already in the MongoDB
    database or objects loaded from the database and then modified in some way.
    As mentioned previously, an explicit *save* call is not strictly necessary
    in the latter case since the MongoDB OML layer tracks changes to modified
    objects and adds them to a *dirty* list of objects that need to be saved
    back to the underlying MongoDB database, either when the next *save* call to
    the application's MongoDB object occurs or the application terminates. An
    explicit *save* call in this case simply provides finer control over when
    database updates occur.

    The method returns *self* as its result. If any errors are encountered, an
    appropriate exception is raised.

**delete()**
    Deletes the object from the associated MongoDB database if possible. If the
    object is not currently stored in the MongoDB database, no action is taken.

    If the object contains *DBLink* or *DBLinks* facets which reference other
    objects stored in the MongoDB database, those objects will be deleted as
    well. This process is recursive, so deleting one top level object may result
    in deleting an entire hierarchy of objects linked together using *DBLink*
    and *DBLinks* references. See the :ref:`understanding` section for more
    information on the role and use of *DBLink* and *DBLinks* facets.

    The method returns *self* as its result. If any errors are encountered, an
    appropriate exception is raised.

**load( query = None, add = False )**
    If *query* is not specified or None, it uses the contents of the object as a
    prototype for matching and loading a single MongoDB database object instance
    that matches the assigned facets of the object. It returns the matching
    object if the load is successful. If no match is found, and *add* is False,
    then None is returned. Otherwise the original object is automatically added
    to the MongoDB database and returned as the result.

    The matching result object, if any, will be of the same class as the object
    or one of its valid subclasses. Valid subclasses are subclasses stored in
    the same MongoDB collection as the object's class. Refer to the
    :ref:`determining` section for more information on how the collection a
    given class is associated with is determined.

    Note that only facet values which have been explicitly set on the prototype
    object are used when finding a match. For example::

        pet = Animal( name = 'Fido' ).load()

    will only use the value of the *name* facet when searching for a match,
    no matter what other attributes are defined on an Animal instance.

    If *query* is a string, it is assumed to be a query string specifying the
    criteria the requested object must match. In this case, the actual contents
    of the object are not use when searching for a match. Refer to the
    :ref:`query_string` section for more information about the format of a valid
    query string.

    If the case where a *query* string is specified, but no match is found and
    *add* is True, the object is added to the MongoDB database and returned as
    the result, just as in the case when no query string is specified.

    Note that unlike the *all* or *iterall* methods, the *load* method will only
    return at most a single matching object and is normally used in cases where
    the requested object is known to be unique.

**all( query = None, skip = 0, limit = 0, sort = None )**
    Uses the contents of the object as a prototype for matching and loading all
    MongoDB database instances which match the assigned facets of the object. It
    returns a list of all matching objects, which may be empty if no matches are
    found.

    Note that the resulting list of objects includes all matching objects that
    are of the same class as the object or one of its valid subclasses. Valid
    subclasses are subclasses stored in the same MongoDB collection as the
    object's class. Refer to the :ref:`determining` section for more information
    on how the collection a given class is associated with is determined.

    If *query* is a string, it is assumed to be a query string specifying the
    criteria that all requested objects must match. In this case, the actual
    contents of the object are not use when searching for matches. Refer to the
    :ref:`query_string` section for more information about the format of a valid
    query string.

    If *sort* is not specified, the returned matching objects are in no
    particular order.

    Since the number of matching MongoDB database objects may potentially be
    very large, you can use the *skip* and *limit* arguments to control how many
    objects are returned:

    * *limit*: An integer specifying the maximum number of objects returned. A
      value of 0 (the default) means return all matching objects.
    * *skip*: An integer specifying the zero-based index of the first matching
      object returned. When combined with *limit*, this can be used with
      multiple calls to *all* to process all matching objects in batches.

**iterall( query = None, skip = 0, limit = 0, sort = None )**
    This method is similar to the *all* method, but returns an iterator that
    yields the next matching MongoDB database instance on each iteration.

    This method can be more efficient than using *all* when the query could
    match a large number of MongoDB database instances but the application only
    needs to process them one at a time. Since the method only converts a single
    MongoDB database document into a Facets-based object on each iterator call,
    the overall latency and memory requirements can be greatly reduced when
    compared to using *all*.

**fetch()**
    Returns the first instance of the class found in the MongoDB database, or
    None if no instances exist. This method is most useful for loading root or
    singleton objects stored in the database.

    The result object, if any, will be of the specified class or one of its
    valid subclasses. Valid subclasses are subclasses stored in the same MongoDB
    collection as the object's class. Refer to the :ref:`determining` section
    for more information on how the collection a given class is associated with
    is determined.

    Note that unlike all of the other methods, this is a class, not an instance
    method. For example::

        pet = Animal.fetch()

    would assign the first Animal instance found in the MongoDB database to
    *pet*.

.. _query_string:

Format of a Query String
------------------------

The *load*, *all* and *iterall* methods each accept an optional *query* string
describing the criteria that matching MongoDB database instances must satisfy.
The MongoDB OML query language is specifically designed to be a cross between
familiar Python language syntax and MongoDB database query semantics.

Although queries are expressed as strings, they are eventually passed to the
Python *eval* function and so must adhere to Python language expression syntax.
In particular, a query should be written as a series of one or more terms
separated by *and* and *or* conjunctions used to control how the individual
terms affect the query result. Due to the way that the query string gets
pre-processed, it is highly recommended that each term be enclosed in
parentheses when using multiple terms. For example::

    "(document == 'War and Peace') and (author == 'Tolstoy')"

Basically, you can think of a valid query string as being something you might
write in a Python *if* statement::

    if (document == 'War and Peace') and (author == 'Tolstoy'):
        do_something

In the case of the MongoDB OML, the *do_something* logic simply adds the current
MongoDB database item to the matching result set. Of course, for performance
reasons, the actual query logic all occurs inside the MongoDB database engine,
which is written in C++, and is translated into the internal query
representation used by MongoDB. But this analogy should help guide you in how to
formulate a valid query string for use with the MongoDB OML.

Each term in the query should be written as an expression returning a boolean
result and may reference facets defined on the current MongoDB database instance
being examined as if they were local variables in the query expression's
evaluation context. For example, given the following class definition::

    class Dog ( MongoDBObject ):
        breed = DBStr
        age   = DBInt

a valid query might be::

    puppies = Dog().all( "(breed == 'Terrier') and (age <= 2)" )

In order to take advantage of the features of the MongoDB query engine, there
are a few special rules to keep in mind when writing query strings:

* You can query for *DBStr* facets that match a regular expression using query
  terms of the form: *name == '/regex/'* or *name != '/regex/'* (e.g.
  *"name == '/x/i'"* matches any name value containing an upper or lower case
  *x*).

  Note that the regular expression uses the Perl */.../* notation, with an
  optional trailing *i* to indicate a case insensitive match. Due to some
  limitations on the query string processor, the actual contents of the regular
  expression (i.e. the part between the leading and trailing slashes) should
  follow standard Python *re* module regular expression syntax.

* You can reference the facets of nested *DBObject* or *DBObjects* values
  directly using standard Python *dot* notation. For example, if you have the
  following class definitions::

      class Person ( MongoDBObject ):
          first_name = DBStr
          last_name  = DBStr

      class Employee ( MongoDBObject ):
          person = DBObject( Person )
          salary = DBFloat

  you could write the following query::

      layoffs = Employee().all(
          "(salary > 100000.00) and (person.last_name == 'Smith')" )

  Not a very fair layoff policy, but a perfectly valid query.

  Note that this rule cannot be used with *DBRef*, *DBRefs*, *DBLink* or
  *DBLinks* values, since their values are not actually available to the MongoDB
  database query engine. Refer to the :ref:`understanding` section for a more
  detailed explanation of the various object reference semantics that MongoDB
  OML supports.

* If you have a *DBObjects* facet containing a list of objects, you can test
  for any element of the list matching a specific subquery using a term of the
  form: *name( subquery )* (e.g.
  *"pets( (breed == 'Terrier') and (age < 5) )"*, which will match if the
  object's list of pets includes at least one whose breed is Terrier with an
  age less than years).

  Note that the previous example is not equivalent to:
  *"(pets.breed == 'Terrier') and (pets.age < 5)"*, since the latter query will
  match any object whose pets list contains at least one object containing a
  breed of Terrier and a possibly different object whose age is less than five
  years. Use the subquery form when the subquery must be true for at least
  one specific item in the list.

  Also note that this rule cannot be used with *DBRefs* and *DBLinks* values,
  since their values are not actually available to the MongoDB database query
  engine. Refer to the :ref:`understanding` section for a more detailed
  explanation of the various object reference semantics that MongoDB OML
  supports.

* If you have a facet whose value is a *DBList* or *DBSet* and you want to query
  if the value contains a specific value, you can write a term of the form:
  *name == [value]* (e.g. *"favorite_numbers == [7]"*). Similarly, if you want
  to check if the value contains at least one of a set of values, you can write:
  *name == [value1,value2,...]* (e.g. *"favorite_numbers == [7,11]"*).

  If you want to make sure that the value does not contain the specified value
  (or values), use *!=* (e.g. *"favorite_numbers != [7,11]"). If you want, you
  can also use *not* instead (e.g. "not (favorite_numbers == [7,11])").

* Similarly, if you have a facet whose value is a *DBList* or *DBSet* and you
  want to query if the value contains every item in a set, you can write a term
  of the form: *name == {value1,value2,...}* (e.g. *"favorite_numbers ==
  {7,11}"*).

  If you want to make sure that it does not contain all specified values, use
  *!=* (e.g. *"favorite_numbers != {7,11}"). As before, you can also use use
  *not* instead (e.g. "not (favorite_numbers == {7,11]}").

* When querying numeric values, you are restricted to using just the standard
  Python comparison operation (==, !=, >, >=, <, <=). The one extension is the
  ability to query with the modulus operator using a term of the form:
  *(name % value1) == value2* or *(name % value1) != value2* (e.g. use
  *(house_number % 2) == 1* to test for an odd house number).

* You can test to make sure that the MongoDB database has a value defined for a
  specific facet by using the facets' *exists* property (e.g. *"age.exists"*).

* You can check the length of a *DBObjects*, *DBRefs* or *DBLinks* facet using
  its *size* property (e.g. *"pets.size == 1"*). Due to a limitation of MongoDB,
  only the *==* and *!=* operators can be used in the query term.

One final note about writing query strings is that even though the string must
be valid Python, being valid Python does not itself guarantee that the MongoDB
database will understand the query. The query string is simply used to translate
a Python-like expression into a form that the MongoDB database can process.
Whether the reulting query returns the objects you expect may require additional
testing and experimentation.

.. _determining:

Determining a Class's Associated MongoDB Collection
---------------------------------------------------

Although a MongoDB database is essentially schema-less, it does allow organizing
groups of related documents into *collections*. The MongoDB OML takes advantage
of this by associating each MongoDBObject subclass with a specific MongoDB
collection. The rules for determing which MongoDB collection a particular
MongoDBObject subclass is associated with are as follows:

* By default, each immediate subclass of MongoDBObject is associated with a
  MongoDB collection having the same name as the subclass. For example, the
  class::

      class IndexDocument ( MongoDBObject ):
          pass

  would be associated with a MongoDB collection having the name *IndexDocument*.

* By default, each non-immediate subclass of MongoDBObject is associated with
  the MongoDB collection of its parent class which is an immediate subclass of
  MongoDBObject. For example, in the following class hierarchy::

      class Animal ( MongoDBObject ):
          pass

      class Dog ( Animal ):
          pass

      class Terrier ( Dog ):
          pass

  the Animal class is associated with the MongoDB *Animal* collection using the
  first rule, and both the Dog and Terrier classes are also associated with the
  MongoDB *Animal* collection through application of the second rule.

* You can explicitly define the MongoDB collection a class is associated with by
  specifying the collection's name using the class-level *collection* attribute.
  For example, the following code::

      class Animal ( MongoDBObject ):
          collection = 'Species'

  associates the Animal class with the MongoDB *Species* collection.

  Explicity defining the associated MongoDB collection also amends the second
  rule above so that subclasses use the explicit MongoDB collection of their
  closest parent class. For example, in the following class hierarchy::

      class Animal ( MongoDBObject ):
          collection = 'Species'

      class Dog ( Animal ):
          collection = 'Dogs'

      class Terrier ( Dog ):
          pass

  instances of Animal are associated with the MongoDB *Species* collection,
  while instances of Dog and Terrier are both associated with the MongoDB *Dogs*
  collection.

Of course, all these rules about the MongoDB collection a class is associated
with are very interesting, but what effect do they have on your application
data model and logic?

In practice, the main effect they have is on the results returned by the various
query methods (i.e. *load*, *all*, *iterall*, *fetch*). In particular, a query
can only return results from the MongoDB collection associated with the query's
object.

For example, given the following class hierarchy::

    class IndexDocument ( MongoDBObject ):
        name = DBStr

    class Animal ( MongoDBObject ):
        name = DBStr

    class Cat ( Animal ):
        pass

    class Dog ( Animal ):
        pass

    class Terrier ( Dog ):
        pass

we have partioned the underlying MongoDB database into two distinct collections:
IndexDocument and Animal. If we perform the following query::

    object = Animal( name = 'Fido' ).load()

we know that we will either get back None or an instance of Animal, Cat, Dog or
Terrier, depending upon whether a match is found in the database or not. We know
that we will not get back an instance of IndexDocument with a *name* of *Fido*,
since IndexDocument instances are not stored in the same MongoDB collection as
Animal, while instances of Cat, Dog and Terrier are.

From this you can see that, just by using the default collection name selected
by the Mongo OML, we get a very natural partitioning of a MongoDB database into
a system supporting a polymorphic object model. If you ask for an Animal, you
will only get a result that is an Animal, even if the result is a subclass of
Animal.

Note also that if we change the above query to::

    object = Dog( name = 'Fido' ).load()

then we know that the result will either be None or an instance of Dog or
Terrier, but not IndexCollection, Animal or Cat. So, in addition to the
partioning provided by the MongoDB collection a class is associated with, the
query mechanism also honors the subtype information implied by the query
object's class. Since in the example the query object was a Dog, the result must
also be a Dog or one of its subclasses, such as Terrier.

As you can see, for many applications you will never need to explicitly set the
MongoDB collection a class is associated with and can safely ignore the
*collection* class attribute. But if the need does arise, the control is there
for you to completely manage the collections that your objects are stored in.

One additional important development consideration is that changing a class's
*collection* attribute does not affect existing objects already stored in a
MongoDB database in the original collection. This problem may be addressed in
the future, but currently the only solution is to either rebuild the MongoDB
database or create a custom *PyMongo*-level script that moves the affected
documents from the original collection to the new collection.

The mongodb Facet
-----------------

In addition to the application facets you define as part of a MongoDBObject
subclass, every MongoDBObject instance also has a special *mongodb* facet which
contains a reference to the *MongoDB* object your application object is
associated with. Refer to the :ref:`mongodb_mongodb` for more detailed
information about the MongoDB object.

In many cases, you will never need to use the *mongodb* facet directly. For
example, there are no references to this facet anywhere in the example
application presented previously. However, the facet does play an important role
in the operation of the MongoDB OML and there may be cases where your application
may need to set or reference it.

If not explicitly set in your application code, the *mongodb* facet is
initialized to the default MongoDB object for your application. However, you are
free to set the value of *mongodb* if necessary. One use case for doing this is
an application that uses two or more MongoDB databases simultaneously. In a
situation like this, you would need to explicitly create each of the MongoDB
object instances needed to access the application's MongoDB databases and then
assign the appropriate MongoDB to the *mongodb* facet of your MongoDBObject
subclass instances as needed.

In practice, this process is not as complex as its sounds. As an example,
imagine that we have an application that uses customer information and credit
card data. For security purposes, all credit card data is stored in a separate,
highly secure, MongoDB database separate from the normal customer information
MongoDB database. For this example, assume we are using the following two
application classes::

    class CreditCard ( MongoDBObject ):
        customer_id        = DBStr
        credit_card_type   = DBStr
        credit_card_number = DBStr
        expiration_date    = DBStr

    class Customer ( MongoDBObject ):
        customer_id = DBStr
        name        = DBStr
        address     = DBStr

where CreditCard objects are stored in the secure MongoDB database, and Customer
objects are kept in the less secure MongoDB database. Assume that our application
has already initialzed access to the two MongoDB databases we are using::

    customer_db    = MongoDB( ... )
    credit_card_db = MongoDB( ... )

and that we now want to retrieve the customer information and credit card data
for *'John Doe'*:

    customer    = Customer( mongodb = customer_db,
                            name    = 'John Doe' ).load()
    credit_card = CreditCard( mongodb     = credit_card_db,
                              customer_id = customer.customer_id ).load()

All we have to do is set the correct MongoDB object on each prototype object
before calling *load* (or *all* or *iterall*) to ensure that the correct
MongoDB database is used. The resulting object (or objects) will then have their
*mongodb* facet correctly set to the MongoDB they were loaded from. A similar
process is used for storing newly created objects in a particular database::

    new_card = CreditCard(
        mongodb            = credit_card_db,
        customer_id        = ...,
        credit_card_type   = ...,
        credit_card_number = ...,
        expiration_date    = ...
    ).save()

