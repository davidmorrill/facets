"""
Defines the various instance descriptors used by the instance editor and
instance editor factory classes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Str, Any, Dict, Tuple, Callable, Bool

from ui_facets \
    import AView

from helper \
    import user_name_for

#-------------------------------------------------------------------------------
#  'InstanceChoiceItem' class:
#-------------------------------------------------------------------------------

class InstanceChoiceItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # User interface name for the item
    name = Str

    # View associated with this item
    view = AView

    # Does this item create new instances?
    is_factory = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def get_name ( self, object = None ):
        """ Returns the name of the item.
        """
        return self.name


    def get_view ( self ):
        """ Returns the view associated with the object.
        """
        return self.view


    def get_object ( self ):
        """ Returns the object associated with the item.
        """
        raise NotImplementedError


    def is_compatible ( self, object ):
        """ Indicates whether a specified object is compatible with the item.
        """
        raise NotImplementedError


    def is_selectable ( self ):
        """ Indicates whether the item can be selected by the user.
        """
        return True


    def is_droppable ( self ):
        """ Indicates whether the item supports drag and drop.
        """
        return False

#-------------------------------------------------------------------------------
#  'InstanceChoice' class:
#-------------------------------------------------------------------------------

class InstanceChoice ( InstanceChoiceItem ):

    #-- Facet Definitions ------------------------------------------------------

    # Object associated with the item
    object = Any

    # The name of the object facet containing its user interface name:
    name_facet = Str( 'name' )

    #-- Public Methods ---------------------------------------------------------

    def get_name ( self, object = None ):
        """ Returns the name of the item.
        """
        if self.name != '':
            return self.name

        name = getattr( self.object, self.name_facet, None )
        if isinstance( name, basestring ):
            return name

        return user_name_for( self.object.__class__.__name__ )


    def get_object ( self ):
        """ Returns the object associated with the item.
        """
        return self.object


    def is_compatible ( self, object ):
        """ Indicates whether a specified object is compatible with the item.
        """
        return ( object is self.object )

#-------------------------------------------------------------------------------
#  'InstanceFactoryChoice' class:
#-------------------------------------------------------------------------------

class InstanceFactoryChoice ( InstanceChoiceItem ):

    #-- Facet Definitions ------------------------------------------------------

    # Indicates whether an instance compatible with this item can be dragged and
    # dropped rather than created
    droppable = Bool( False )

    # Indicates whether the item can be selected by the user
    selectable = Bool( True )

    # A class (or other callable) that can be used to create an item compatible
    # with this item
    klass = Callable

    # Tuple of arguments to pass to **klass** to create an instance
    args = Tuple

    # Dictionary of arguments to pass to **klass** to create an instance
    kw_args = Dict( Str, Any )

    # Does this item create new instances? This value overrides the default.
    is_factory = True

    #-- Public Methods ---------------------------------------------------------

    def get_name ( self, object = None ):
        """ Returns the name of the item.
        """
        if self.name != '':
            return self.name

        name = getattr( object, 'name', None )
        if isinstance( name, basestring ) and (name.strip() != ''):
            return name

        if issubclass( type( self.klass ), type ):
            klass = self.klass
        else:
            klass = self.get_object().__class__

        return user_name_for( klass.__name__ )


    def get_object ( self ):
        """ Returns the object associated with the item.
        """
        return self.klass( *self.args, **self.kw_args )


    def is_droppable ( self ):
        """ Indicates whether the item supports drag and drop.
        """
        return self.droppable


    def is_compatible ( self, object ):
        """ Indicates whether a specified object is compatible with the item.
        """
        if issubclass( type( self.klass ), type ):
            return isinstance( object, self.klass )

        return isinstance( object, self.get_object().__class__ )


    def is_selectable ( self ):
        """ Indicates whether the item can be selected by the user.
        """
        return self.selectable

#-------------------------------------------------------------------------------
#  'InstanceDropChoice' class:
#-------------------------------------------------------------------------------

class InstanceDropChoice ( InstanceFactoryChoice ):

    #-- Facet Definitions ------------------------------------------------------

    # Indicates whether an instance compatible with this item can be dragged and
    # dropped rather than created . This value overrides the default.
    droppable = True

    # Indicates whether the item can be selected by the user. This value
    # overrides the default.
    selectable = False

    # Does this item create new instances? This value overrides the default.
    is_factory = False

#-- EOF ------------------------------------------------------------------------