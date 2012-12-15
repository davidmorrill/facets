"""
Defines the IAbstractLayout interface which any GUI toolkit neutral layout
manager must implement.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Interface, Any

#-------------------------------------------------------------------------------
#  'IAbstractLayout' interface:
#-------------------------------------------------------------------------------

class IAbstractLayout ( Interface ):
    """ The interface that any GUI toolkit neutral layout manager must
        implement.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The underlying GUI toolkit specific layout manager:
    layout = Any

    #-- Interface Methods ------------------------------------------------------

    def calculate_minimum ( self ):
        """ Calculates the minimum size needed by the layout manager.
        """


    def perform_layout ( self, x, y, dx, dy ):
        """ Layout the contents of the layout manager based on the specified
            size and position.
        """


    def add ( self, item ):
        """ Adds an adapted item to the layout.
        """

#-- EOF ------------------------------------------------------------------------