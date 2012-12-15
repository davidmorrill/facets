"""
Defines the GraphicsTextCell class used for rendering the contents of a
GraphicsText object as an IDataCell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance

from facets.ui.graphics_text \
    import GraphicsText

from facets.ui.data.api \
    import DataCell

#-------------------------------------------------------------------------------
#  'GraphicsTextCell' class:
#-------------------------------------------------------------------------------

class GraphicsTextCell ( DataCell ):
    """ Defines the GraphicsTextCell class used for rendering the contents of a
        GraphicsText object as an IDataCell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The GraphicsText object this cell renders:
    graphics_text = Instance( GraphicsText )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Paints the contents of the cell into the graphics context specified
            by *g*. The area the cell should be painted into is specified by the
            current value of the 'bounds' attribute.
        """
        self.graphics_text.draw( g, *self.bounds )

    #-- Facet Default Values ---------------------------------------------------

    def _size_default ( self ):
        return self.graphics_text.size( self.graphics )

#-- EOF ------------------------------------------------------------------------
