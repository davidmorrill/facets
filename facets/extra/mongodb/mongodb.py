"""
Defines the MongoDB class used to represent and manage a MongoDB database.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import atexit
import sys

from weakref \
    import WeakValueDictionary

from time \
    import sleep

from subprocess \
    import Popen, PIPE, STDOUT

from pymongo \
    import Connection

from pymongo.errors \
    import AutoReconnect

from facets.api \
    import HasPrivateFacets, Str, Int, Bool, Range, Instance, Any, View, \
           Tabbed, VGroup, Item, FacetError

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The MondoDB document key used to stored an object's type index:
TYPE_INDEX = '?'

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

# The global 'implicit' MongoDB object:
_mongodb = None

def mongodb ( db = None ):
    """ Gets/Sets the implicit MongoDB object to use for the current
        application. If *db* is not None, it sets the database to use to *db*.
        Otherwise, it returns the current implicit database. If no implicit
        database has been set, it creates one.
    """
    global _mongodb

    if db is not None:
        if not isinstance( db, MongoDB ):
            raise FacetError( 'The argument must be a MongoDB instance.' )

        _mongodb = db

    if _mongodb is None:
        _mongodb = MongoDB()

    return _mongodb


def mongodb_save ( ):
    """ Saves any outstanding database objects when an application terminates.
    """
    global _mongodb

    if _mongodb is not None:
        if _mongodb.connection is not None:
            _mongodb.save()
            _mongodb.close()

        _mongodb.shutdown()

# Register a handler to be called when the application terminates:
atexit.register( mongodb_save )

#-------------------------------------------------------------------------------
#  'MongoDB' class:
#-------------------------------------------------------------------------------

class MongoDB ( HasPrivateFacets ):
    """ Defines the class representing a MongoDB connection.
    """

    #-- Facet Definitions -- Configuration Parameters --------------------------

    # The host the MongoDB database is running on:
    host = Str( 'localhost' )

    # The port the MongoDB database is running on:
    port = Int( 27017 )

    # The name of the MongoDB database to use:
    database = Str( 'facets' )

    # The maximum size limit for the connection pool:
    max_pool_size = Int( 10 )

    # Timeout (in seconds) to use for socket operations (default is no timeout):
    network_timeout = Range( 0, 60, 0 )

    # Are datetime instances timezone aware? If True, datetime instances
    # returned as values in a document by this Connection will be timezone aware
    # (otherwise they will be naive):
    tz_aware = Bool( False )

    # Use 'getlasterror' for each write operation?
    safe = Bool( False )

    # Should write operations block until they have been commited to the
    # journal? Ignored if the server is running without journaling. Implies
    # safe = True:
    journal = Bool( False )

    # Create the connection to the server using SSL?
    ssl = Bool( False )

    # Should the application attempt to automatically start a local copy of the
    # MongoDB server if it cannot create a connection?
    auto_start = Bool( True )

    # Should the application automatically stop a local copy of the MongoDB
    # server started by 'auto_start' when the application terminates?
    auto_stop = Bool( True )

    #-- Facet Definitions ------------------------------------------------------

    # The PyMongo Connection object to the MongoDB:
    connection = Instance( Connection, transient = True )

    # The PyMongo Database object for the connection:
    db = Any # Instance( pymongo.database )

    # The Popen object for the MongoDB database process when auto-start is used
    # to automatically start the MongoDB database:
    process = Any

    # The MongoDB document containing all of the type information stored in the
    # database:
    types = Any( transient = True )

    # Mapping from fully-qualified class name to type index:
    # { 'package.module.class': type_index }
    type_map = Any( {}, transient = True )

    # Mapping from type index to the list of type indices for known subclasses
    # of the type:
    # { type_index: [ type_index, ... ] }
    subtype_map = Any( {}, transient = True )

    # Mapping from fully qualified class name to class:
    # { 'package.module.class': class }
    class_map = Any( {}, transient = True )

    # Mapping from MongoDBObject class to the collection used to hold its
    # instances: { klass: collection }
    collection_map = Any( {}, transient = True )

    # The collection used to manage the list of defined MongoDBObject classes:
    types_collection = Any( transient = True ) # Instance( Collection )

    # Set of all 'dirty' MongoDBObjects that need to be saved to the database:
    dirty = Any( set(), transient = True )

    # Cache of all currently loaded MongoDB database objects:
    # WeakValueDictionary of { ( _id, type_index ): object }
    cache = Any( transient = True )

     #-- Facet View Definitions -------------------------------------------------

    view = View(
        Tabbed(
            VGroup(
                Item( 'host',
                      tooltip = 'The name of the MongoDB host'
                ),
                Item( 'port',
                      tooltip = 'The port number of the MongoDB host'
                ),
                Item( 'database',
                      tooltip = 'The name of the MongoDB database to use'
                ),
                label = 'Basic'
            ),
            VGroup(
                Item( 'auto_start',
                      label   = 'Auto-start server',
                      tooltip = 'Automatically start a local MongoDB server if '
                                'it is not running'
                ),
                Item( 'auto_stop',
                      label   = 'Auto-stop server',
                      tooltip = 'Automatically stop a local MongoDB server '
                                'started using auto-start'
                ),
                Item( 'max_pool_size',
                      label   = 'Maximum pool size',
                      tooltip = 'The maximum size limit for the connection pool'
                ),
                Item( 'network_timeout',
                      tooltip = 'Timeout (in seconds) to use for socket '
                                'operations (0 = No timeout)'
                ),
                Item( 'tz_aware',
                      label   = 'Time zone aware',
                      tooltip = 'Are datetime instances timezone aware?'
                ),
                Item( 'safe',
                      label   = 'Use safe writes',
                      tooltip = "Use 'getlasterror' for each write operation?"
                ),
                Item( 'journal',
                      tooltip = 'Should write operations block until they have '
                                'been commited to the journal?'
                ),
                Item( 'ssl',
                      label   = 'Use SSL',
                      tooltip = 'Create the connection to the server using SSL?'
                ),
                label = 'Advanced'
            ),
        ),
        id      = 'facets.extra.mongodb.mongodb.MongoDB',
        title   = 'MongoDB Configuration',
        buttons = [ 'OK', 'Cancel' ],
        kind    = 'modal'
    )

    #-- Facet Default Values ---------------------------------------------------

    def _connection_default ( self ):
        # The following connections options are not currently supported:
        # w, wtimeout, fsync, replicaSet, socketTimeoutMS, connectTimeoutMS,
        # read_preference.

        retries = 0
        while True:
            try:
                return Connection(
                    host            = self.host,
                    port            = self.port,
                    max_pool_size   = self.max_pool_size,
                    network_timeout = self.network_timeout or None,
                    tz_aware        = self.tz_aware,
                    safe            = self.safe,
                    journal         = self.journal,
                    ssl             = self.ssl
                )
            except AutoReconnect:
                if (not self.auto_start) or (self.host != 'localhost'):
                    return None

                if retries == 0:
                    try:
                        self.process = Popen(
                            'mongod', stdout = PIPE, stderr = STDOUT
                        )
                        self.process.stdout.close()
                        retries = 1
                    except:
                        return None
                else:
                    retries += 1
                    if retries > 40:
                        return None

                    sleep( 0.25 )


    def _db_default ( self ):
        return self.connection[ self.database ]


    def _types_default ( self ):
        types = self.types_collection.find_one()
        if types is None:
            types = { 'types': [], 'indices': {} }

        return types


    def _types_collection_default ( self ):
        return self.db[ TYPE_INDEX ]


    def _cache_default ( self ):
        return WeakValueDictionary()

    #-- Public Methods ---------------------------------------------------------

    def save ( self, *objects ):
        """ Saves all of the the MongoDBObject instances specified by *objects*
            to the associated MongoDB database. If *dbobject* is an empty list,
            any currently 'dirty' objects are synchronized with the database.
        """
        if len( objects ) == 0:
            objects = list( self.dirty )

        #print '--- Saving %d objects -------------------------' % len( objects )

        for object in objects:
            object.save()

        #print '--- End Saving -------------------------------------------------'

        # Return the number of objects saved:
        return len( objects )


    def close ( self ):
        """ Closes the associated MongoDB database.
        """
        self.connection.close()
        del self.connection

        return self


    def shutdown ( self ):
        """ Shuts down the MongoDB database process if it was started by the
            application.
        """
        if self.auto_stop and (self.process is not None):
            self.process.terminate()

        self.process = None

        return self


    def reset ( self ):
        """ Resets the contents of the database to an empty state.
        """
        db = self.db
        for collection in db.collection_names():
            if ((collection != TYPE_INDEX) and
                (not collection.startswith( 'system.' ))):
                db.drop_collection( collection )

        # Reset all internal state:
        self.cache.clear()
        self.dirty.clear()

        return self


    def configure ( self, application = 'default', force = False ):
        """ Allows the user to interactively configure the MongoDB database
            connection information.

            The configuration information is looked up in and saved to the
            Facets database using the application name specified by
            *application*. If *force* is True, the user is always prompted for
            the configuration information, using the existing configuration data
            as the default if it already exists. Otherwise, the user is only
            prompted for the configuration information if it is not already in
            the Facets database.
        """
        edit = True
        db   = self.facet_db_get( application )
        if isinstance( db, MongoDB ):
            self.copy_facets( db )
            edit = force

        if edit and self.edit_facets().result:
            self.facet_db_set( application, self )

        return self

    #-- Private Methods --------------------------------------------------------

    def add_dirty ( self, object ):
        """ Adds the MongoDBObject specified by *object* to the list of 'dirty'
            objects that need to be written to the database.
        """
        self.dirty.add( object )


    def remove_dirty ( self, object ):
        """ Removes the MongoDBObject specified by *object* from the list of
            'dirty' objects waiting to be written to the database.
        """
        self.dirty.discard( object )


    def register_cache ( self, object ):
        """ Registers the MongoDBObject specified by *object* with the cache.
        """
        if object._id is not None:
            self.cache[ ( object._id, object.mongodb_type ) ] = object


    def check_cache ( self, *key ):
        """ Returns the MongoDBObject (if any) currently in the cache with the
            specified *key.
        """
        return self.cache.get( key )


    def collection_for ( self, klass ):
        """ Returns the MongoDB collection to use for the MongoDBObject subclass
            specified by *klass*.
        """
        collection = self.collection_map.get( klass )
        if collection is None:
            self.collection_map[ klass ] = collection = \
                self.db[ klass.collection ]

        return collection


    def type_for ( self, klass, update = True ):
        """ Returns the document type for the MongoDBObject subclass specified
            by *klass*. The document type is an index into the list of known
            MongoDBObject classes stored in the database and is used when
            reloading a document to convert it to the correct MongoDBObject
            class type.

            The *update* flag indicates whether or not the underlying MongoDB
            database information should be updated or not, and is provided to
            minimize the number of database updates needed when recursive calls
            are made.
        """
        # Get the fully qualified class name:
        fqn = '%s.%s' % ( klass.__module__, klass.__name__ )

        # Check to see if the type information for the class has already been
        # defined in this session:
        type_map = self.type_map
        type     = type_map.get( fqn )
        if type is None:
            indices = self.types[ 'indices' ]
            types   = self.types[ 'types' ]
            try:
                # Check to see if the database knows about the class type:
                type     = types.index( fqn )
                str_type = str( type )
            except:
                # If the information is not in the MongoDB database, add it:
                types.append( fqn )
                self.class_map[ fqn ] = klass
                type_map[ fqn ]       = type = len( types ) - 1
                str_type              = str( type )
                indices[ str_type ]   = {}

            # Create or destroy any changed collection indices as specified by
            # the class metadata collected when the class was defined:
            old_indices         = indices[ str_type ]
            new_indices         = klass.mongodb_indices.copy()
            indices[ str_type ] = klass.mongodb_indices
            for index_name, index_info in old_indices.iteritems():
                if index_info != new_indices.get( index_name ):
                    self.collection_for( klass ).drop_index( index_name )
                    update = True
                else:
                    del new_indices[ index_name ]

            for index_name, index_info in new_indices.iteritems():
                self.collection_for( klass ).create_index( index_info[0],
                    unique = index_info[1],
                    name   = index_name
                )
                update = True

            # Save the type information back in the MongoDB database if needed:
            if update:
                self.save_type_info()

        # Return the type index for the class:
        return type


    def object_for ( self, document ):
        """ Returns the MongoDBObject corresponding to a specified MongoDB
            database *document*. If *document* is None, None is returned.
        """
        if document is None:
            return None

        klass = self.class_for( document[ TYPE_INDEX ] )

        return klass( mongodb = self ).mongodb_load( document )


    def class_for ( self, type_index ):
        """ Returns the class object for the specified *type_index*.
        """
        name  = self.types[ 'types' ][ type_index ]
        klass = self.class_map.get( name )
        if klass is None:
            module_name, class_name = name.rsplit( '.', 1 )
            module = sys.modules.get( module_name )
            if module is None:
                __import__( module_name )
                module = sys.modules.get( module_name )

            self.class_map[ name ] = klass = module.__dict__[ class_name ]

        return klass


    def add_type_for ( self, klass, document = None ):
        """ Adds the type information for the class specified by *klass* to the
            MongoDB search document specified by *document*. Returns the updated
            document as the result. *klass* can either be a MongoDBObject
            subclass or an integer representing the index of an existing
            MongoDBObject subclass already in the MongoDB database.
        """
        if document is None:
            document = {}

        type = klass
        if not isinstance( type, int ):
            type = self.type_for( klass )

        document[ TYPE_INDEX ] = {
            '$in': self.subtypes_for( type )
        }

        return document


    def subtypes_for ( self, type_index ):
        """ Returns a list of the valid subtype indices for the type index
            specified by *type_index*.
        """
        subtypes = self.subtype_map.get( type_index )
        if subtypes is None:
            self.subtype_map[ type_index ] = subtypes = []
            class_for = self.class_for
            klass     = class_for( type_index )
            for type in xrange( len( self.types[ 'types' ] ) ):
                if issubclass( class_for( type ), klass ):
                    subtypes.append( type )

        return subtypes


    def save_type_info ( self ):
        """ Saves the current type information back to the MongoDB database.
        """
        self.types_collection.save( self.types, manipulate = True )


    def fetch ( self, klass, document = None ):
        """ Returns the first instance of the MongoDBObject class (or any of its
            subclasses) specified by *klass*. *klass* can either be a
            MongoDBObject subclass or an integer representing the index of an
            existing MongoDBObject subclass already in the MongoDB database.
        """
        type = klass
        if isinstance( klass, int ):
            klass = self.class_for( klass )

        return self.object_for(
            self.collection_for( klass ).find_one(
                self.add_type_for( type, document )
            )
        )

#-- EOF ------------------------------------------------------------------------
