"""
Defines the UIInfo class used to represent the object and editor content of
    an active Facets-based user interface.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Instance, Constant, Bool

#-------------------------------------------------------------------------------
#  'UIInfo' class:
#-------------------------------------------------------------------------------

class UIInfo ( HasPrivateFacets ):
    """ Represents the object and editor content of an active Facets-based
        user interface
    """

    #-- Facet Definitions ------------------------------------------------------

    # Bound to a UI object at UIInfo construction time
    ui = Instance( 'facets.ui.ui.UI', allow_none = True )

    # Indicates whether the UI has finished initialization
    initialized = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def bind_context ( self ):
        """ Binds all of the associated context objects as facets of the
            object.
        """
        for name, value in self.ui.context.items():
            self.bind( name, value )


    def bind ( self, name, value, id = None ):
        """ Binds a name to a value if it is not already bound.
        """
        if id is None:
            id = name

        if not hasattr( self, name ):
            self.add_facet( name, Constant( value ) )
            if id != '':
                self.ui._names.append( id )

#-- EOF ------------------------------------------------------------------------