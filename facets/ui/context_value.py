"""
Defines some helper classes and facets used to define 'bindable' editor
values.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Instance, Str, Int, Float, Either

#-------------------------------------------------------------------------------
#  'ContextValue' class:
#-------------------------------------------------------------------------------

class ContextValue ( HasPrivateFacets ):
    """ Defines the name of a context value that can be bound to some editor
        value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The extended facet name of the value that can be bound to the editor
    # (e.g. 'selection' or 'handler.selection'):
    name = Str

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, name ):
        """ Initializes the object.
        """
        self.name = name

# Define a shorthand name for a ContextValue:
CV = ContextValue

#-------------------------------------------------------------------------------
#  Facet definitions useful in defining bindable editor facets:
#-------------------------------------------------------------------------------

InstanceOfContextValue = Instance( ContextValue, allow_none = False )

def CVType ( type ):
    return Either( type, InstanceOfContextValue, sync_value = 'to' )

CVInt   = CVType( Int )
CVFloat = CVType( Float )
CVStr   = CVType( Str )

#-- EOF ------------------------------------------------------------------------