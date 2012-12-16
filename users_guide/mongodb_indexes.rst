.. _mongodb_indexes:

Defining Indexes
================

As a performance tuning aid, the MongoDB OML allows you to turn any database
facet, or group of database facets, into a MongoDB index. 

Indexes typically are used to improve the performance of queries which only
return a small fraction of all possible objects. Queries that return a
relatively large percentage of all available objects typically do not see
performance improvements when an index is added.

In addition, adding an index slows performance when adding, deleting or updating
objects in the database, since both the object data and the associated index
data must be updated.

You create an index simply my adding *index* metadata to any *DBxxx* facet
defined in a MongoDBObject subclass. If you recall, our example application
included the following class definition::
    
    class IndexWord ( MongoDBObject ):
        word      = DBStr( index = True )
        count     = DBInt
        documents = DBSet
    
where we have added a MongoDB index for the IndexWord class's *word* facet.

There are actually several different ways to specify *index* metadata. The 
simplest method is to simply set *index = True*, which defines a simple, 
ascending order, non-unique index of the specified facet.

You can also specify a more detailed description of the type of index you want
to create using a value of the form:
*index = '[ascending|descending] [unique] [name] [nnn]'*

where:

**ascending|descending**
    Specifies the sort order used by the index. If not specified, the sort order
    defaults to *ascending*.
    
**unique**
    Specifies that all index values must be unique (i.e. no duplicate values are
    allowed). Attempting to add a duplicate value to the index will raise an
    exception. If *unique* is not explicitly specified, the default is to allow 
    duplicate (non-unique) values in the index.

**name**
    Specifies the name to give the index within the MongoDB database. The name
    is also used to group related facets when defining a multi-facet index (see
    the next item). If not specified, the MongoDB database automatically creates
    a name for you based on the associated facet names.
    
**nnn**
    Specifies the index of the facet within a multi-value index. That is, you
    can create indexes based upon more than a single object facet. In such
    cases, the facet values are added to the composite index in the order
    specified by the *nnn* values.
    
    If you are creating a multi-facet index, make sure that each facet's *index*
    metadata uses the same *name* value, since the *name* value is used to
    determine which facets belong to the same index. The *nnn* value is then
    used to define the position of a particular facet within the set of facets
    defining the index.
    
    Note that the *nnn* values can have gaps. The values are only used to
    perform an ascending order sort used for ordering all of the facets within
    the composite index.
    
The values in the *index* metadata can be specified in any order. For example,
the following index definitions are all equivalent::
    
    name = DBStr( index = 'ascending unique my_index 1' )
    name = DBStr( index = '1 my_index unique' )
    name = DBStr( index = 'unique 1 ascending my_index' )
    
Indexes can be both added and removed. Indexes are added when the MongoDB OML
discovers *index* metadata on database facets which did not previously have an
index. Similarly, existing indexes are deleted when the MongoDB OML detects that
no *index* metadata is present on database facets which previously had an index
defined.

The indexes are added or deleted as soon as the change is discovered. So if you
already have a database with 10,000,000 objects in it and decide to add an index
to one of the object facets, you may see a possibly long delay the next time you
run your application as MongoDB adds the index to the database, since it will
have to create an index entry for each object already in the database.

