"""
Describe the module function here...
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

    #-- 'IWidget' interface ----------------------------------------------------

    control = Any
    parent  = Any

    #-- 'IWidget' Interface ----------------------------------------------------

    def destroy ( self ):
        self.control = None

#-- EOF ------------------------------------------------------------------------