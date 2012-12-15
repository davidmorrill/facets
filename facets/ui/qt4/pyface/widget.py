"""
The toolkit specific implementation of a Widget. See the IWidget interface for
the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, HasFacets, implements

from facets.ui.pyface.i_widget \
    import IWidget, MWidget

#-------------------------------------------------------------------------------
#  'Widget' class:
#-------------------------------------------------------------------------------

class Widget ( MWidget, HasFacets ):
    """ The toolkit specific implementation of a Widget. See the IWidget
        interface for the API documentation.
    """

    implements( IWidget )

    #-- IWidget Interface ------------------------------------------------------

    control = Any
    parent  = Any

    #-- IWidget Interface ------------------------------------------------------

    def destroy ( self ):
        if self.control is not None:
            self.control.setParent( None )
            self.control = None

#-- EOF ------------------------------------------------------------------------