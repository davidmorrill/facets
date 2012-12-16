The MongoDB OML
===============

The MongoDB OML (Object Management Layer) is a Facets package that allows you
to persist, query, update and delete collections and hierarchies of Facets-based
objects in an external MongoDB database using a very simple and straightforward
Facets and Python based programming model. In fact, the model is basically the
standard Facets model with a small number of new classes and facet types added.

In case you are not already familiar with it, MongoDB is one of the more
popular examples of the new class of schema-less, document oriented databases
that have sprung up over the last few years. Because these databases are not
based on the relational model which has dominated the database landscape for 
the last several decades, this relatively new category of database is sometimes
referred to as a *No SQL* database.

Because of its schema-less, document centric design, MongoDB is well suited for
use as a persistent storage layer for object oriented applications. Combined
with the metadata and change notification framework that Facets provides, the
MongoDB OML provides a very simple and natural framework for implementing
object oriented applications with a persistent object storage system.

There are many examples of using a relational database as the storage mechanism
for object oriented applications. The software layer used to map objects to a
relational database is often referred to as an *ORM* (*Object Relational Mapping
(or Model*)). Because MongoDB is not based on the relational model, we have
instead chosen to call the software layer an *OML* (*Object Mapping Layer*).

There are a wide variety of techniques for saving and restoring Python objects
to external storage of some sort, some available as part of the core Python
application, and some as separately installable packages. While we will not
attempt to compare and contrast all of the available approaches, in this section
we will present some of the more compelling reasons for using the MongoDB OML,
and then let you make you own decision about which approach or package to use.

**It's easy to use**
    For the most part, using the MongoDB OML is no different than using the
    rest of the Facets package. If you are already comfortable with the Facets 
    style of programming, then using MongoDB OML requires almost no effort. The
    complete example presented in the next section helps illustrates this point 
    quite effectively we think.
    
**It supports large amounts of data**
    MongoDB is a real database, and as a result can easily support storing and
    retrieving huge amounts of data without requiring that all of the data
    first be loaded into memory.
    
**It supports object-oriented query**
    Individual objects or collections of objects can be easily retrieved from
    a MongoDB using a very simple and straightforward Facets and Python based
    query mechanism. This can be a very important feature when dealing with
    extremely large object collections.
    
**It's fast**
    One of the reasons for choosing MongoDB over some of the other new *No SQL*
    databases is its reputation for being very fast at storing and retrieving
    data.
    
**It's flexible and easy to set up**
    Another noteworthy characteristic of MongoDB is its relative ease in setting
    up and administering a database. The MongoDB OML extends this by making use
    of the database almost completely transparent to the developer as well.

If this brief introduction to the MongoDB OML and its feature set have got you
in the least bit interested, please continue on with some of the more in
depth sections, starting with a complete, multi-tool, MongoDB-based application
example.

.. toctree::
   :maxdepth: 1

   mongodb_example
   mongodb_installing
   mongodb_mongodbobject
   mongodb_facets
   mongodb_mongodb
   mongodb_indexes
   mongodb_limitations
   
