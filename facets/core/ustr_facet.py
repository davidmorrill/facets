"""
Defines the UStr type and HasUniqueStrings mixin class for efficiently
creating lists of objects containing facets whose string values must be
unique within the list.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.facet_base \
    import is_str

from facets.core.has_facets \
    import HasFacets

from facets.core.facet_value \
    import FacetValue, TypeValue

from facets.core.facet_types \
    import List

from facets.core.facet_handlers \
    import FacetType, NoDefaultSpecified

#-------------------------------------------------------------------------------
#  'UStr' class:
#-------------------------------------------------------------------------------

class UStr ( FacetType ):
    """ Facet type that ensures that a value assigned to a facet is unique
        within the list it belongs to.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The type value to assign to restore the original list item type when a
    # list item is removed from the monitored list:
    str_type = FacetValue()

    # The informational text describing the facet:
    info_text = 'a unique string'

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, owner, list_name, str_name,
                         default_value = NoDefaultSpecified, **metadata ):
        """ Initializes the type.
        """
        super( UStr, self ).__init__( default_value, **metadata )

        self.owner     = owner
        self.list_name = list_name
        self.str_name  = str_name
        self.ustr_type = TypeValue( self )
        self.names     = dict( [ ( getattr( item, str_name ), item )
                                 for item in getattr( owner, list_name ) ] )
        self.roots     = {}
        self.available = {}
        owner.on_facet_set( self._items_modified, list_name + '[]' )


    def validate ( self, object, name, value ):
        """ Ensures that a value being assigned to a facet is a unique string.
        """
        if isinstance( value, basestring ):
            names    = self.names
            old_name = getattr( object, name )
            if names.get( old_name ) is object:
                self._remove( old_name )

            if value not in names:
                names[ value ] = object
                return value

            available = self.available.get( value )
            while True:
                if available is None:
                    new_value = None
                    break

                index = available.pop()
                if len( available ) == 0:
                    del self.available[ value ]
                    available = None

                new_value = '%s_%d' % ( value, index )
                if new_value not in names:
                    break

            if new_value is None:
                self.roots[ value ] = index = \
                    self.roots.setdefault( value, 1 ) + 1
                new_value = '%s_%d' % ( value, index )

            names[ new_value ] = object
            return new_value

        self.error( object, name, value )

    #-- Private Methods --------------------------------------------------------

    def _remove ( self, name ):
        """ Removes a specified name.
        """
        self.names.pop( name, None )
        col = name.rfind( '_' )
        if col >= 0:
            try:
                index  = int( name[ col + 1: ] )
                prefix = name[ : col ]
                if prefix in self.roots:
                    if prefix not in self.available:
                        self.available[ prefix ] = set()
                    self.available[ prefix ].add( index )
            except:
                pass

    def _items_modified ( self, removed, added ):
        """ Handles items being added to or removed from the monitored list.
        """
        str_name  = self.str_name
        str_type  = self.str_type
        ustr_type = self.ustr_type

        for item in removed:
            setattr( item, str_name, str_type )
            self._remove( getattr( item, str_name ) )

        for item in added:
            setattr( item, str_name, ustr_type )
            setattr( item, str_name, getattr( item, str_name ) )

#-------------------------------------------------------------------------------
#  'HasUniqueStrings' class:
#-------------------------------------------------------------------------------

class HasUniqueStrings ( HasFacets ):
    """ Mixin or base class for objects containing lists with items containing
        string valued facets that must be unique.

        List facets within the class that contain items which have string facets
        which must be unique should indicate this by attaching metadata of the
        form:
            unique_string = 'facet1, facet2, ..., facetn'
        where each 'faceti' value is the name of a facet within each list item
        that must contain unique string data.

        For example:
            usa = List( State, unique_string = 'name, abbreviation' )
    """

    #-- Private Facets ---------------------------------------------------------

    # List of UStr facets that have been attached to object list facets:
    _ustr_facets = List

    #-- HasFacets Object Initializer -------------------------------------------

    def facets_init ( self ):
        """ Adds any UStrMonitor objects to list facets with 'unique_string'
            metadata.
        """
        super( HasUniqueStrings, self ).facets_init()

        for name, facet in self.facets( unique_string = is_str ).items():
            for str_name in facet.unique_string.split( ',' ):
                self._ustr_facets.append( UStr( self, name, str_name.strip() ) )

            items = getattr( self, name )
            if len( items ) > 0:
                setattr( self, name, [] )
                setattr( self, name, items )

#-- EOF ------------------------------------------------------------------------