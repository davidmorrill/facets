"""
Defines the set of standard Facets available for use in defining persistent
facets in a MongoDBObject subclass. Only facets from this module can be used to
define values that will be stored in a MongoDB database. Other facet types will
be treated as transient data that are not stored in the database.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from facets.api \
    import FacetType, Any, Bool, Int, Float, Range, Str, List, Dict, Set, \
           Instance, FacetError

from facets.core.facet_collections \
    import FacetListObject

from facets.core.facet_base \
    import Missing

from dbobject \
    import MongoDBObject

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Value returned when a DBRef has no defined value:
NoRef = ( None, None, None )

#-------------------------------------------------------------------------------
#  Simple MongoDB data type facets:
#-------------------------------------------------------------------------------

# Any simple value (Bool, Int, Float, Str, ...):
DBAny = Any( mongodb_value = 'simple' )

# Boolean value:
DBBool = Bool( mongodb_value = 'simple' )

# Integer value:
DBInt = Int( mongodb_value = 'simple' )

# Floating point value:
DBFloat = Float( mongodb_value = 'simple' )

# String value:
DBStr = Str( mongodb_value = 'simple' )

# List of heterogeneous simple data values (Bool, Int, Float, Str, ...):
DBList = List( mongodb_value = 'simple', mongodb_items = True )

# Dictionary of heterogeneous simple data values:
DBDict = Dict( mongodb_value = 'simple', mongodb_items = True )

# Set of heterogeneous simple data values:
DBSet = Set( mongodb_value = 'set', mongodb_items = True )

# Range of numeric values:
def DBRange ( low = None, high = None, value = None,
              exclude_low = False, exclude_high = False, **metadata ):
    metadata[ 'mongodb_value' ] = 'simple'

    return Range( low, high, value, exclude_low, exclude_high, **metadata )

#-------------------------------------------------------------------------------
#  'DBObject' facet definition:
#-------------------------------------------------------------------------------

class DBObject ( Instance ):
    """ Defines an instance of a MongoDBObject value owned by the containing
        object.
    """

    def __init__ ( self, klass = MongoDBObject, factory = None, args = None,
                         kw = None, allow_none = True, adapt = None,
                         module = None, **metadata ):
        """ Initializes the object.
        """
        metadata.setdefault( 'mongodb_value',  'object' )
        metadata.setdefault( 'mongodb_object', True )

        super( DBObject, self ).__init__(
            klass      = klass,
            factory    = factory,
            args       = args,
            kw         = kw,
            allow_none = allow_none,
            adapt      = adapt,
            module     = module,
            **metadata
        )

#-------------------------------------------------------------------------------
#  'DBObjects' facet definition:
#-------------------------------------------------------------------------------

class DBObjects ( List ):
    """ Defines a list of MongoDBObjects owned by the containing object.
    """

    def __init__ ( self, facet = MongoDBObject, value = None,
                         minlen = 0, maxlen = sys.maxint, items = True,
                         **metadata ):
        """ Initlializes the object.
        """
        metadata.setdefault( 'mongodb_value',   'objects' )
        metadata.setdefault( 'mongodb_objects', True )
        metadata.setdefault( 'mongodb_items',   True )

        super( DBObjects, self ).__init__(
            facet  = facet,
            value  = value,
            minlen = minlen,
            maxlen = maxlen,
            items  = items,
            **metadata
        )

#-------------------------------------------------------------------------------
#  'DBRef' facet definition:
#-------------------------------------------------------------------------------

class DBRef ( FacetType ):
    """ Defines an instance of a MongoDBObject value not owned by the containing
        object.
    """
    metadata = { 'mongodb_value': 'ref', 'mongodb_items': True }


    def __init__ ( self, klass = MongoDBObject, **metadata ):
        self.klass = klass

        super( DBRef, self ).__init__( **metadata )


    def get ( self, object, name ):
        id, type, db_object = getattr( object, '_' + name, NoRef )
        if db_object is None:
            if id is not None:
                db_object = object.mongodb.fetch( type, { '_id': id } )
                setattr( object, '_' + name, ( id, type, db_object ) )

        return db_object


    def set ( self, object, name, value ):
        if not isinstance( value, self.klass ):
            raise FacetError(
                ("The value of the '%s' facet of a %s instance must be a "
                 "%s instance, but a value of %s was specified") %
                ( name, object.__class__.__name__, self.klass.__name__, value )
            )

        xname     = '_' + name
        new_value = ( value._id, value.mongodb_type, value )
        old_value = getattr( object, xname, NoRef )
        if new_value[:2] != old_value[:2]:
            setattr( object, xname, ( value._id, value.mongodb_type, value ) )
            object.facet_property_set( name, old_value[2] )

#-------------------------------------------------------------------------------
#  'FacetListObject' class:
#-------------------------------------------------------------------------------

class RefsListObject ( FacetListObject ):

    #-- Public Methods ---------------------------------------------------------

    def __getitem__ ( self, key ):
        value = FacetListObject.__getitem__( self, key )
        if isinstance( value, tuple ):
            value = self.object().mongodb.fetch( value[1], { '_id': value[0] } )
            list.__setitem__( self, key, value )

        return value


    def __getslice__ ( self, i, j ):
        getitem = self.__getitem__

        return [ getitem( k )
                 for k in xrange( max( 0, i ),
                                  min( max( 0, j ), len( self ) ) ) ]


    def __repr__ ( self ):
        return self.__getslice__( 0, len( self ) ).__repr__()


    def _values ( self, values = Missing ):
        if values is Missing:
            return list.__getslice__( self, 0, len( self ) )
        else:
            list.__setslice__( self, 0, 0, values )

#-------------------------------------------------------------------------------
#  'DBRefs' facet definition:
#-------------------------------------------------------------------------------

class DBRefs ( List ):
    """ Defines a list of MongoDBObject values not owned by the containing
        object.
    """
    default_value_class = RefsListObject


    def __init__ ( self, facet = MongoDBObject, value = None,
                         minlen = 0, maxlen = sys.maxint, items = True,
                         **metadata ):
        """ Initializes the object.
        """
        self._init_metadata( metadata )

        super( DBRefs, self ).__init__(
            facet  = facet,
            value  = value,
            minlen = minlen,
            maxlen = maxlen,
            items  = items,
            **metadata
        )


    def _init_metadata ( self, metadata ):
        """ Initializes the metadata for the facet.
        """
        metadata.setdefault( 'mongodb_value', 'refs' )

#-------------------------------------------------------------------------------
#  'DBLink' facet definition:
#-------------------------------------------------------------------------------

class DBLink ( DBRef ):
    """ Defines an instance of a MongoDBObject value owned by the containing
        object but which is not loaded until referenced.
    """
    metadata = { 'mongodb_value': 'link' }


    def set ( self, object, name, value ):
        if not isinstance( object, MongoDBObject ):
            raise FacetError(
                ("The value of the '%d' facet of a %s instance must be a "
                 "MongoDBObject instance, but a value of %s was specified") %
                ( name, object.__class__.__name__, value )
            )

        xname     = '_' + name
        new_value = ( value._id, value.mongodb_type, value )
        old_value = getattr( object, xname, NoRef )
        if new_value[:2] != old_value[:2]:
            id, type, old_object = old_value
            if (old_object is None) and (id is not None):
               old_object = object.mongodb.fetch( type, { '_id': id } )

            if old_object is not None:
                old_object.delete()

            setattr( object, xname, new_value )
            object.facet_property_set( name, old_object )

#-------------------------------------------------------------------------------
#  'DBLinks' facet definition:
#-------------------------------------------------------------------------------

class DBLinks ( DBRefs ):
    """ Defines a list of MongoDBObject values owned by the containing object
        but not loaded until referenced.
    """

    def _init_metadata ( self, metadata ):
        """ Initializes the metadata for the facet.
        """
        metadata.setdefault( 'mongodb_value', 'links' )
        metadata.setdefault( 'mongodb_links', True )

#-- EOF ------------------------------------------------------------------------
