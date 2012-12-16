.. _mongodb_facets:

MongoDB OML Facets
==================

The MongoDB OML allows storing objects which are subclasses of the MongoDBObject
class in a MongoDB database. However, only the object attributes defined using
the facets described in this section are actually stored in the database. All
other object facets are simply discarded when the object is stored in the
database.

All of the special MongoDB OML facets can be imported from
*facets.extra.mongodb.api* and have names of the form *DBxxx* to help make their
special database semantics stand out better when reading a class definition. In
addition, most of the facets have semantics identical to other, standard facets
that they are based on. In cases such as this, the facet name is formed simply
by prepending the *DB* prefix to the standard facet name (e.g. *DBStr*).

The remainder of this section provides a brief description of all of the
available MongoDB OML facets. A follow-on section then provides additional
details about those MongoDB OML facets that have more complex database specific
semantics.

**DBAny**
    Any simple value (Bool, Int, Float, Str, ...). It has the same semantics as
    the standard *Any* facet.
    
    Note however that it should not be used for saving object references. Use
    the *DBObject*, *DBRef* or *DBLink* facet instead.

**DBBool**
    A boolean value. It has the same semantics as the standard *Bool* facet.

**DBInt**
    An integer value. It has the same semantics as the standard *Int* facet.

**DBFloat**
    A floating point value. It has the same semantics as the standard *Float* 
    facet.

**DBStr**
    A string value. It has the same semantics as the standard *Str* facet.

**DBList**
    A list of heterogeneous simple data values (Bool, Int, Float, Str, ...). It
    has the same semantics as the standard *List* facet.
    
    Note however that it should not be used to store object references. Use a
    *DBObjects*, *DBRefs* or *DBLinks* facet instead.

**DBDict**
    A dictionary of heterogeneous simple data values. It has the same semantics
    as the standard *Dict* facet.
    
    Note however that it should not be used to store object references.
    Currently there is no way using the MongoDB OML to store database object
    references using a dictionary-based value.

**DBSet**
    A set of heterogeneous simple data values. It has the same semantics as the
    standard *Set* facet.
    
    Note however that it should not be used to store object references.
    Currently there is no way using the MongoDB OML to store database object
    references using a set-based value.

**DBRange**
    A numeric value within a specified range. It has the same semantics as the
    standard *Range* facet.

**DBObject**
    Contains a reference to a MongoDBObject instance that is stored as part of
    the containing object in the MongoDB database. It has the same semantics as
    the standard *Instance* facet, although the specified class should be 
    MongoDBObject or a subclass.

**DBObjects**
    Contains a list of references to MongoDBObject instances that are stored as
    part of the containing object in the MongoDB database. It has the same 
    semantics as the standard *List* facet, although the default facet has been
    changed to MongoDBObject. If the list facet type is explicitly specified, it 
    should be MongoDBObject or a subclass.

**DBRef**
    Contains a reference to a MongoDBObject instance that is not owned by the
    referencing object and is stored independently of the referencing object in
    the MongoDB database. It has semantics similar to the standard *Instance* 
    facet, although the specified class should be MongoDBObject or a subclass.

**DBRefs**
    Contains a list of references to MongoDBObject instances that are not owned
    by the referencing object and which are stored independently of the
    referencing object in the MongoDB database. It has the same semantics as the
    standard *List* facet, although the default facet has been changed to
    MongoDBObject. If the list facet type is explicitly specified, it should be
    MongoDBObject or a subclass.

**DBLink**
    Contains a reference to a MongoDBObject instance that is owned by the
    referencing object but is stored independently of the referencing object in
    the MongoDB database. It has semantics similar to the standard *Instance* 
    facet, although the specified class should be MongoDBObject or a subclass.

**DBLinks**
    Contains a list of references to MongoDBObject instances that are owned by
    the referencing object but which are stored independently of the referencing
    object in the MongoDB database. It has the same semantics as the standard
    *List* facet, although the default facet has been changed to MongoDBObject.
    If the list facet type is explicitly specified, it should be MongoDBObject
    or a subclass.

.. _understanding:

Understanding DBObject(s), DBRef(s) and DBLinks(s)
--------------------------------------------------

If you've already read the preceding section on the MongoDB OML facets, you've
probably noticed the perhaps confusing variety of facets provided for storing
database object references. In this section we hope to dispel as much of that
confusion as possible by explaining in detail the various nuances between the
various object reference facets and why they exist.

As you've presumably already gathered, there are three basic object reference 
types: *DBObject*, *DBRef* and *DBLink*, along with their corresponding list
forms: *DBObjects*, *DBRefs*, *DBLinks*.

In each case the difference between the singular and plural forms is the same.
The singular form holds a single object reference, while the list form holds a
list of object references which may contain zero, one or more object references.
That difference affects how you use them within your Python code, but as far as
the MongoDB OML layer is concerned, the singular and plural form both have the
same semantics. Since it is the MongoDB OML semantics we are concerned with in
this section, we will not make any further distinction between the singular and
plural forms in the remainder of this discussion.

So now the question becomes what is the semantic difference between *DBObject*,
*DBRef* and *DBLink*. All of them accept the same types of values, namely
MongoDBObject (or one of its subclasses) instances. The differences lie in how
they are stored in the underlying MongoDB database and how the MongoDB OML layer
handles them.

If we were simply pickling a large object hierarchy and storing the result in a
file, we wouldn't need to make any distinction between a *DBObject*, *DBRef* or
*DBLink*. We would simply serialize each object in the object graph as we
encountered it, and write the entire resulting byte stream out to a file. When
we unpickle the object graph, we would simply reverse the process by reading the
entire file and reconstructing the original object graph.

The problem with this approach is time and memory. As the size of the object
graph increases, the time required to load, and amount of memory needed to hold,
all of the objects might eventually reach unacceptable levels.

This is one of many reasons why developers often turn to storing their data in
a database of some sort. Databases are typically designed to store huge amounts
of data and provide quick access to only those parts of the data needed by
an application at any particular instant.

One of the major design goals of the MongoDB OML is to provide quick access to
huge amounts of stored data while still preserving the convenience of defining
and using an object oriented data model. And the approach it takes is to
recognize that there is no "one size fits all" solution to mapping an object
model onto an underlying database, and to provide several solutions that 
developers can choose from when creating their data model. Hence the need for 
the *DBObject*, *DBRef* and *DBLink* facets. Each provides nearly identical
data modeling semantics, but provide different performance and size trade offs 
when looked at from the underlying database storage layer point of view.

So in what follows we'll be looking at various common use cases and what effect
the different MongoDB OML object reference facets might have when applied in
those cases.

Owned Versus Shared Data
------------------------

*Owned* data is data specific to a single object, while *shared* data is data
that is shared among a group of objects. A simple example might be that of a
grade school student. Each student has their own name (which is data they own)
and a teacher (which is data they do not own, but share with other students).

In terms of mapping objects to a database, owned data is typically stored as
part of the data associated with the owning object, while shared data is not.
Instead, shared data is typically stored separately in the database, and any
object sharing that data simply stores a reference to where the shared data
is kept in the database.

This is the primary distinction between *DBObject* and *DBLink* facets, which
are used for *owned* data, and *DBRef* facets, which are used for *shared*
data.

Management of owned data is simple. Since it is stored as part of the owning
object, deleting the owning object also deletes the owned data.

Shared data, on the other hand, is more complex to manage. Since shared data is
usually shared among an unknown number of other objects, it's often difficult to
tell exactly when shared data should be deleted. There must usually be some
additional application logic that deals explicitly with creating and deleting
shared objects.

In the case of the MongoDB OML, shared objects are represented using *DBRef*
(and *DBRefs*) facets. In general, using these facets means that it is up to
your application code to determine when it is time to delete the object the
facets reference (actually, you usually want to delete them only when no object
continues to reference them). The same is true about making sure that shared
objects are correctly added to the database, although an object containing a
*DBRef* that refers to an shared object not in the database will automatically
save the shared object to the database when the object containing the *DBRef*
is saved.

Now that we've made the distinction between *owned* and *shared* object
references, let's proceed with a further refinement of the *owned* data use 
case.

Immediate Versus Deferred Access
--------------------------------

As we've seen, *owned* data is logically part of the owning object and is 
deleted when the owning object is deleted. However, in practical terms, we can
make a further distinction between two different types of owned data: 
*immediate* and *deferred*.

As an example, let's take the case of an application containing information
about a server farm. Each object representing a server might contain information
about the server's hostname, IP address and a log of all server activity for the
last month.

Now each of these three pieces of information is data *owned* by the server
object, since it all applies to the specific server it is associated with. If we
ever delete a server object, we should delete all of its owned data as well. The
problem is that the log data may be very large and seldom used by most
applications using the MongoDB database containing the server data, and so it
seems very inefficient in terms of time and memory to load all of the log data
every time an application instantiates a server object from the database.

The MongoDB OML helps you address this problem by providing both *immediate* and
*deferred* object references. An *immediate* reference is an object whose data
is loaded into storage at the same time its owning object is loaded. A
*deferred* reference is an object which is not loaded into storage until the
application code that loads the owning object actually references the
*deferred* object.

With this distinction in mind, it should now be clear that we would probably
want the server hostname and IP address to be defined as *immediate* data,
since they are fairly small and used often by applications, while the server
log data should be *deferred*, since it is large and infrequently used by
applications.

In MongoDB OML, all facets except for *DBRef(s)* and *DBLink(s)* are *immediate*
mode facets. Both *DBRef(s)* and *DBLink(s)* facets are *deferred* mode, meaning
that their associated object data is not loaded until explicitly referenced by
application code.

So now we can proceed with a possible definition of our hypothetical server
object classes::

    class LogData ( MongoDBObject ):
        data = List( Str )
        
    class Server ( MongoDBObject ):
        hostname   = DBStr
        ip_address = DBStr
        log        = DBLink( LogData )
        
We've used a *DBLink* facet rather than a *DBRef* facet because the LogData
object is *owned* by the Server object, and we want it to be deleted
automatically when a Server object is deleted. But because *DBLink* is also a
*deferred* facet, we know that the LogData object will never be loaded into
memory unless some application code explicitly references it. For example::

    for item in server.log.data:
        print item

Now that we've explained the distinctions between *owned* and *shared* data,
and between *immediate* and *deferred* access, it might be useful to provide a
table showing how these concepts apply to the various MongoDB OML facets:

========= ======= =========
Facet     Data Is Access Is
========= ======= =========
DB...     Owned   Immediate
DBObject  Owned   Immediate
DBObjects Owned   Immediate
DBLink    Owned   Deferred
DBLinks   Owned   Deferred
DBRef     Shared  Deferred
DBRefs    Shared  Deferred
========= ======= =========

where *DB...* refers to the *DBAny*, *DBBool*, *DBInt*, *DBFloat*, *DBStr*,
*DBList*, *DBDict*, *DBSet* and *DBRange* facets.

Finally, let's finish up this section with a couple of additional tips about the
trade-offs in using the various MongoDB OML object reference types:

* The facets of *DBObject(s)* object references can be used in *query strings*
  (e.g. *"employee.first_name == 'Jack'"*, where *first_name* is a facet of the
  *employee DBObject* facet), while the facets of *DBRef(s)* and *DBLink(s)*
  object references cannot. 
  
  The reason for this is that *DBObject(s)* facets store their data directly in
  the owning object's MongoDB database representation, where it can be accessed
  directly by the MongoDB query engine. Both *DBRef(s)* and *DBLink(s)* facets
  only store object reference information in the referencing object's MongoDB
  database representation. The actual object data is stored separately in the
  database and is not directly accessible to the query engine.
  
* Since *DBLink(s)* facets defer the storage and time penalty of loading 
  referenced objects until they are actually used by an application, it might 
  seem like using *DBLink(s)* facets would always be more efficient than using 
  *DBObject(s)* facets. In practice, the actual storage and time efficiency
  probably depends heavily on the size and access patterns of the data involved.
  
  If any of the object data is always accessed by applications, then deferring
  the object load may actually be slower than loading it with the owning object
  since multiple database requests are required to load the separate objects.
  Plus there is the additional database storage overhead required for saving
  the database object reference in the owning object.

