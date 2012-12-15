"""
Defines the MongoDBObject base class used to represent a Facets-based object
that can be stored in a MongoDB collection.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pymongo \
    import ASCENDING, DESCENDING

from facets.api \
    import HasFacets, MetaHasFacets, Any, Instance, Property, on_facet_set

from facets.core.facet_base \
    import Undefined

from mongodb \
    import MongoDB, mongodb, TYPE_INDEX

from dbquery \
    import query_from_string

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def mongodb_facet ( value ):
    """ Returns True if the value is not a valid MongoDB facet, and False
        otherwise.
    """
    return (value is not None)


def normalized_index ( name, index ):
    """ Returns a normalized tuple of the form:
            ( name, ordering, unique, index_name, i ) ), where:
            - name       = name of the facet being indexed.
            - ordering   = 'ascending' or 'descending' (sort order for index).
            - index_name = name of the index.
            - i          = order of the facet within a compound index.
        The possible forms of *index* are:
        - True = ( name, 'ascending', False, name, 0 )
        - 'ascending'  = ( name, 'ascending', False, name, 0 )
        - 'descending' = ( name, 'descending' False, name, 0 )
        - 'unique'     = ( name, 'ascending', True, name, 0 )
        - 'nnn'        = ( name, 'ascending', False, name, nnn )
        - 'xxx'        = ( name, 'ascending', False, xxx, 0 )
        - Combination of the above (except for True) in any order.
    """
    result = [ name, 'ascending', False, name, 0 ]
    if isinstance( index, basestring ):
        for word in index.split():
            if word in ( 'ascending', 'descending' ):
                result[1] = word
            elif word == 'unique':
                result[2] = True
            else:
                try:
                    result[4] = int( word )
                except:
                    result[3] = word

    return tuple( result )


def index_info_for ( indices ):
    """ Returns a dictionary of information used to create or drop a MongoDB
        index. The dictionary is of the form:
        { 'index_name': [ [ ( key, direction ) ... ], unique ] }
    """
    result = {}
    for name, ordering, unique, index_name, i in indices:
        info = result.setdefault( index_name, [ [], False ] )
        info[0].append( ( name, OrderingMap[ ordering ] ) )
        info[1] = info[1] or unique

    return result


def document_to_object ( db_object, document ):
    """ Attempts to convert and return the MongoDB document specified by
        *document* to its corresponding MongoDBObject object within the context
        of the MongoDBObject specified by *db_object*. If the document is not a
        valid MongoDB document, it simply returns the original document.
    """
    if isinstance( document, dict ) and (TYPE_INDEX in document):
        document = db_object.mongodb.object_for( document )

    return document


def document_to_ref ( document ):
    """ Attempts to convert and return the MongoDB document specified by
        *document* to its corresponding internal reference format, which is a
        tuple of the form: ( _id, type_index ). If *document* is None, None is
        returned.
    """
    if document is None:
        return None

    return ( document[ '_id' ], document[ TYPE_INDEX ] )


def object_to_document ( object ):
    """ Attempts to convert and return the MongoDBObject specified by *object*
        to a MongoDB document. If it is not a MongoDBObject, *object* is
        returned.
    """
    if isinstance( object, MongoDBObject ):
        return object.mongodb_document

    return object


def save_simple ( db_object, name ):
    """ Returns the 'simple'-style value for the *name* facet of the *db_object*
        MongoDBObject object for saving as part of a MongoDB document.
    """
    return getattr( db_object, name )


def load_simple ( db_object, name, value ):
    """ Assigns the 'simple'-style MongoDB document value *value* to the *name*
        facet of the *db_object* MongoDBObject object.
    """
    setattr( db_object, name, value )


def save_set ( db_object, name ):
    """ Returns the 'set'-style value for the *name* facet of the *db_object*
        MongoDBObject object for saving as part of a MongoDB document.
    """
    return list( getattr( db_object, name ) )


def load_set ( db_object, name, value ):
    """ Assigns the 'set'-style MongoDB document value *value* to the *name*
        facet of the *db_object* MongoDBObject object.
    """
    setattr( db_object, name, set( value ) )


def save_object ( db_object, name ):
    """ Returns the 'object'-style value for the *name* facet of the *db_object*
        MongoDBObject object for saving as part of a MongoDB document.
    """
    return object_to_document( getattr( db_object, name ) )


def load_object ( db_object, name, document ):
    """ Assigns the 'object'-style MongoDB document value *object* to the *name*
        facet of the *db_object* MongoDBObject object.
    """
    setattr( db_object, name, document_to_object( db_object, document ) )


def save_objects ( db_object, name ):
    """ Returns the 'objects'-style value for the *name* facet of the *db_object*
        MongoDBObject object for saving as part of a MongoDB document.
    """
    return [ object_to_document( object )
             for object in getattr( db_object, name ) ]


def load_objects ( db_object, name, objects ):
    """ Assigns the 'objects'-style MongoDB document value *objects* to the
        *name* facet of the *db_object* MongoDBObject object.
    """
    setattr( db_object, name, [ document_to_object( db_object, object )
                                for object in objects ] )


def save_ref ( db_object, name ):
    """ Returns the 'ref/link'-style value for the *name* facet of the
        *db_object* MongoDBObject object for saving as part of a MongoDB
        document.
    """
    from dbfacets import NoRef

    xname = '_' + name
    id, type, object = getattr( db_object, xname, NoRef )
    if (object is not None) and (id is None):
        # The owning object is being saved with a link that is not yet in the
        # MongoDB database, so save the linked object to the database so that
        # the owning object can record its database id correctly (then update
        # the owning object state accordingly):
        object.save()
        id   = object._id
        type = object.mongodb_type
        setattr( db_object, xname, ( id, type, object ) )

    return ( id, type )


def load_ref ( db_object, name, id ):
    """ Assigns the 'ref'-style MongoDB document value *object* to the *name*
        facet of the *db_object* MongoDBObject object.
    """
    # Note that this code bypasses triggering a facet notification to prevent
    # forcing the object reference to be loaded when the owning object is
    # loaded:
    setattr( db_object, '_' + name, ( id[0], id[1], None ) )


def save_refs ( db_object, name ):
    """ Returns the 'refs/links'-style value for the *name* facet of the
        *db_object* MongoDBObject object for saving as part of a MongoDB
        document.
    """
    result = []
    for i, object in enumerate( getattr( db_object, name )._values() ):
        if isinstance( object, MongoDBObject ):
            if object._id is None:
                object.save()

            result.append( { '_id':      object._id,
                             TYPE_INDEX: object.mongodb_type } )
        elif object is not None:
            result.append( { '_id': object[0], TYPE_INDEX: object[1] } )
        else:
            result.append( object )

    return result


def load_refs ( db_object, name, objects ):
    """ Assigns the 'objects'-style MongoDB document value *objects* to the
        *name* facet of the *db_object* MongoDBObject object.
    """
    getattr( db_object, name )._values( [ document_to_ref( object )
                                          for object in objects ] )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from 'mongodb_value' facet metadata to a database 'save' function:
MongoDBSave = {
    'set':     save_set,
    'object':  save_object,
    'objects': save_objects,
    'ref':     save_ref,
    'refs':    save_refs,
    'link':    save_ref,    # Note: same as 'ref'
    'links':   save_refs    # Note: same as 'refs'
}

# Mapping from 'mongodb_value' facet metadata to a database 'load' function:
MongoDBLoad = {
    'set':     load_set,
    'object':  load_object,
    'objects': load_objects,
    'ref':     load_ref,
    'refs':    load_refs,
    'link':    load_ref,    # Note: same as 'ref'
    'links':   load_refs    # Note: same as 'refs'
}

# Mapping from 'ascending'/'descending' to equivalent PyMongo ordering:
OrderingMap = {
    'ascending':  ASCENDING,
    'descending': DESCENDING,
}

#-------------------------------------------------------------------------------
#  'MongoDBObject' class:
#-------------------------------------------------------------------------------

class MongoDBObject ( HasFacets ):
    """ Defines the MongoDBObject base class representing a Facets-based object
        that can be stored in a MongoDB collection.
    """

    #-- Class Variables --------------------------------------------------------

    # The set of MongoDB-related facets for the class:
    # mongodb_facets = { name: facet, ... }
    # mongodb_notify = set( name, ... )
    # mongodb_link   = [ name, ... ]
    # mongodb_links  = [ name, ... ]

    # The name of the MongoDB collection to use for this class:
    # collection = 'name'

    # The type index for the class within the MongoDB:
    # _mongodb_type = Int

    #-- Facet Definitions ------------------------------------------------------

    # The MongoDB collection id for the object:
    _id = Any

    #-- Private Facet Definitions ----------------------------------------------

    # The MongoDB object associated with this instance:
    mongodb = Instance( MongoDB )

    # The MongoDBObject instance that 'owns' this instance:
    mongodb_owner = Any

    # The MongoDB collection to use for this object:
    mongodb_collection = Property

    # The MongoDB document derived from this object:
    mongodb_document = Property

    # The type index for the class within the MongoDB:
    mongodb_type = Property

    #-- Facet Default Values ---------------------------------------------------

    def _mongodb_default ( self ):
        return mongodb()

    #-- Property Implementations -----------------------------------------------

    def _get_mongodb_document ( self ):
        # Create the document from the MongoDB-related facets:
        result = dict(
            [ ( name, facet.mongodb_save( self, name ) )
              for name, facet in self.mongodb_facets.iteritems() ]
        )

        # Set the document type (used when reloading saved documents):
        result[ TYPE_INDEX ] = self.mongodb_type

        # Add the document id if it is defined:
        if self._id is not None:
            result[ '_id' ] = self._id

        # Return the document:
        return result


    def _get_mongodb_type ( self ):
        type = self.__class__._mongodb_type
        if type is None:
            type = self.__class__._mongodb_type = self.mongodb.type_for(
                self.__class__
            )

        return type


    def _get_mongodb_collection ( self ):
        return self.mongodb.collection_for( self.__class__ )

    #-- Public Methods ---------------------------------------------------------

    def save ( self ):
        """ Saves the object to its corresponding MondoDB database collection.
        """
        #print 'save:', self

        id = self.mongodb_collection.save(
            self.mongodb_document, manipulate = True
        )
        if self._id is None:
            self._id = id
            self.mongodb.register_cache( self )

        self.mongodb.remove_dirty( self )

        return self


    def delete ( self ):
        """ Deletes the object from the associated MongoDB database if possible.
        """
        if self._id is not None:
            # Delete the object:
            self.mongodb_collection.remove( { '_id': self._id } )

            # Recursively delete all owned objects:
            for name in self.mongodb_link:
                object = getattr( self, name )
                if object is not None:
                    object.delete()

            # Recursively delete all lists of owned objects:
            for name in self.mongodb_links:
                for object in getattr( self, name ):
                    object.delete()

        return self


    def load ( self, query = None, add = False ):
        """ Uses the contents of the object as a prototype for matching and
            loading a MongoDB document that matches the assigned facets of the
            object. It returns the matching object if the load is successful. If
            no match is found, and *add* is False, then None is returned.
            Otherwise the original object is returned and automatically added to
            the MongoDB database.
        """
        document = self.mongodb_collection.find_one(
            self._mongodb_query_document( query )
        )
        if document is None:
            if not add:
                return None

            self.save()

            return self

        return self.mongodb_load( document )


    def all ( self, query = None, skip = 0, limit = 0, sort = None ):
        """ Uses the contents of the object as a prototype for matching and
            loading all MongoDB documents that match the assigned facets of the
            object. Returns a list of all matching objects, which may be empty
            if no matching objects are found.
        """
        return [ object for object in self.iterall( query, skip, limit, sort ) ]


    def iterall ( self, query = None, skip = 0, limit = 0, sort = None ):
        """ Similar to the 'all' method, but returns an iterator that yields the
            next MongoDBObject matching the query on each iteration.

            This method is useful when the query could match a large number of
            objects in the MongoDB database, but the application only needs to
            process them one at a time, since it only instantiates each object
            when needed.
        """
        klass = self.__class__

        #print 'all:', self._mongodb_query_document( query )

        for document in self.mongodb_collection.find(
            self._mongodb_query_document( query ),
            skip = skip, limit = limit, sort = sort
        ):
            yield klass().mongodb_load( document )


    def mongodb_load ( self, document ):
        """ Initializes an object using the specified MongoDB database
            dictionary *document*.
        """
        db     = self.mongodb
        id     = document.get( '_id' )
        object = db.check_cache( id, self.mongodb_type )
        if object is not None:
            return object

        for name, facet in self.mongodb_facets.iteritems():
            value = document.get( name, Undefined )
            if value is not Undefined:
                facet.mongodb_load( self, name, value )

        self._id = id
        db.register_cache( self )
        db.remove_dirty(   self )

        return self

    #-- Facet Event Handlers ---------------------------------------------------

    def _anyfacet_set ( self, facet ):
        """ Handles any facet of the object being changed.
        """
        if facet in self.mongodb_notify:
            object = self
            owner  = self.mongodb_owner
            if owner is not None:
                object = owner
                if object.mongodb_owner is not None:
                    self.mongodb_owner = object = object.mongodb_owner

            if object._id is not None:
                object.mongodb.add_dirty( object )


    @on_facet_set( '+mongodb_object' )
    def _object_modified ( self, old, new ):
        """ Handles a DBObject facet being changed.
        """
        if isinstance( old, MongoDBObject ):
            old.mongodb_owner = None

        if isinstance( new, MongoDBObject ):
            owner = self.mongodb_owner
            if owner is not None:
                new.mongodb_owner = owner
            else:
                new.mongodb_owner = self


    @on_facet_set( '+mongodb_objects[]' )
    def _objects_modified ( self, removed, added ):
        """ Handles a DBObjects facet being changed.
        """
        for object in removed:
            if isinstance( object, MongoDBObject ):
                object.mongodb_owner = None

        for object in added:
            if isinstance( object, MongoDBObject ):
                owner = self.mongodb_owner
                if owner is not None:
                    object.mongodb_owner = owner
                else:
                    object.mongodb_owner = self


    @on_facet_set( '+mongodb_links[]' )
    def _links_modified ( self, removed, added ):
        """ Handles a DBLinks facet being changed.
        """
        for object in removed:
            if (object is not None) and (object not in added):
                object.delete()

    #-- Private Methods --------------------------------------------------------

    def _mongodb_query_document ( self, query = None ):
        """ Returns a MongoDB document that can be used to search for objects
            matching the explicitly assigned facets of the object.
        """
        if not isinstance( query, basestring ):
            facets = self.mongodb_facets
            search = dict( [ ( name, getattr( self, name ) )
                               for name in self.__dict__.iterkeys()
                               if name in facets ] )
        else:
            search = query_from_string( query )

        return self.mongodb.add_type_for( self.__class__, search )

    #-- Class Methods ----------------------------------------------------------

    @classmethod
    def fetch ( klass ):
        """ Returns the first instance of the class found in the MongoDB
            database, or None if no instances exist. This method is most useful
            for loading root or singleton objects stored in the database.
        """
        return mongodb().fetch( klass )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def new_mongodbobject_class ( klass ):
    """ Handles a new MongoDBObject subclass being created.
    """
    if issubclass( klass, MongoDBObject ):
        # Create the set of MongoDB-related facets:
        items   = []
        indices = []
        link    = []
        links   = []
        facets  = klass.class_facets( mongodb_value = mongodb_facet )
        for name, facet in facets.iteritems():
            value              = facet.mongodb_value
            facet.mongodb_save = MongoDBSave.get( value, save_simple )
            facet.mongodb_load = MongoDBLoad.get( value, load_simple )
            if facet.mongodb_items:
                items.append( name + '_items' )

            if value == 'link':
                link.append( name )
            elif value == 'links':
                links.append( name )

            index = facet.index
            if index is not None:
                indices.append( normalized_index( name, index ) )

        klass.mongodb_facets  = facets
        klass.mongodb_notify  = set( facets.keys() + items )
        klass.mongodb_link    = link
        klass.mongodb_links   = links
        klass.mongodb_indices = index_info_for( sorted(
            indices, key = lambda x: '%s_%02d' % ( x[3], x[4] )
        ) )

        # Get the name of the MongoDB collection to use for this class:
        name = getattr( klass, 'collection', None )
        if not isinstance( name, basestring ):
            klass.collection = klass.__name__

        # Initialize various class-level variables that will be correctly
        # initialized later on first use:
        klass._mongodb_type = None

# Add the new MongoDBObject subclass listener to the HasFacets meta-class:
MetaHasFacets.add_listener( new_mongodbobject_class )

#-- EOF ------------------------------------------------------------------------
