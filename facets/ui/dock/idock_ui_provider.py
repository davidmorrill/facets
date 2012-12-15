"""
Defines the IDockUIProvider interface which objects which support being dragged
and dropped into a DockWindow must implement.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Interface

#-------------------------------------------------------------------------------
#  'IDockUIProvider' class:
#-------------------------------------------------------------------------------

class IDockUIProvider ( Interface ):

    #-- IDockUIProvider Interface ----------------------------------------------

    def get_dockable_ui ( self, parent ):
        """ Returns a Facets UI which a DockWindow can imbed.
        """

#-- EOF ------------------------------------------------------------------------