"""
Defines the ControlCell class used for rendering a Control object as an
IDataCell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Property, Instance, Control, property_depends_on

from facets.ui.data.api \
    import DataCell

#-------------------------------------------------------------------------------
#  'ControlCell' class:
#-------------------------------------------------------------------------------

class ControlCell ( DataCell ):
    """ Defines the ControlCell class used for rendering a Control object as an
        IDataCell.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The minimum size needed to render the cell's contents specified as a tuple
    # of the form ( width, height ) (override):
    size = Property # ( Tuple( Int, Int ) )

    # The Control object this cell renders:
    control = Instance( Control )

    #-- Public Methods ---------------------------------------------------------

    def paint ( self, g ):
        """ Paints the contents of the cell into the graphics context specified
            by *g*. The area the cell should be painted into is specified by the
            current value of the 'bounds' attribute.

            The Control handles its own painting, since it is a separate
            control, so this method does not need to do anything.
        """

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'control:min_size' )
    def _get_size ( self ):
        return self.control.min_size

    #-- Facet Event Handlers ---------------------------------------------------

    def _bounds_set ( self, bounds ):
        """ Handles the 'bounds' facet being changed.
        """
        self.control.bounds = bounds

#-- EOF ------------------------------------------------------------------------
